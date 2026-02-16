# Model Serving Architectures on Kubernetes

This reference covers production-grade inference serving architectures, from simple API wrappers to enterprise platforms.

## Architecture Comparison

| Framework | Use Case | Complexity | Pros | Cons |
|-----------|----------|-----------|------|------|
| **FastAPI + Gunicorn** | Single model API | Low | Simple, lightweight, easy to debug | Limited batching, no multi-model |
| **vLLM** | LLM inference | Low-Medium | Fast (paged attention), auto-batching | GPU-only, needs tuning |
| **TGI (Text Generation)** | LLM inference | Medium | Production-ready, streaming, quantization | Inference-only, less flexible |
| **Triton Inference Server** | Multi-model ensemble | High | Multi-framework, GPU optimization, ensemble | Complex YAML, performance tuning |
| **Ray Serve** | Distributed inference | High | Auto-scaling, traffic splitting, composable | More memory overhead |
| **KServe** | Enterprise ML | Very High | Model versioning, canary, auto-scaling | Steeper learning curve |

---

## 1. FastAPI + Gunicorn (Simple Single Model)

**Best for**: Small models, development, simple inference APIs

### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app
RUN pip install --no-cache-dir fastapi uvicorn gunicorn torch transformers

COPY app.py .

EXPOSE 8000
CMD ["gunicorn", "--workers=2", "--worker-class=uvicorn.workers.UvicornWorker", \
     "--bind=0.0.0.0:8000", "app:app"]
```

### app.py
```python
from fastapi import FastAPI
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

app = FastAPI()
model = None
tokenizer = None

@app.on_event("startup")
async def load_model():
    global model, tokenizer
    model = AutoModelForCausalLM.from_pretrained("mistralai/Mistral-7B-Instruct-v0.1")
    tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-Instruct-v0.1")
    if torch.cuda.is_available():
        model = model.cuda()

@app.post("/generate")
async def generate(prompt: str, max_tokens: int = 100):
    inputs = tokenizer(prompt, return_tensors="pt")
    if torch.cuda.is_available():
        inputs = {k: v.cuda() for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model.generate(**inputs, max_new_tokens=max_tokens)

    return {"text": tokenizer.decode(outputs[0])}
```

### Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: llm-fastapi
spec:
  replicas: 2
  template:
    spec:
      containers:
      - name: api
        image: my-llm:latest
        resources:
          limits:
            nvidia.com/gpu: 1
          requests:
            nvidia.com/gpu: 1
        ports:
        - containerPort: 8000
        startupProbe:
          httpGet:
            path: /docs
            port: 8000
          failureThreshold: 60
          periodSeconds: 5
```

---

## 2. vLLM (High-Performance LLM Serving)

**Best for**: LLM inference with high throughput, auto-batching needed

### Dockerfile
```dockerfile
FROM nvcr.io/nvidia/pytorch:24.02-py3

WORKDIR /app
RUN pip install --no-cache-dir vllm

COPY requirements.txt .
RUN pip install -r requirements.txt

EXPOSE 8000
CMD ["python", "-m", "vllm.entrypoints.api_server", \
     "--model", "meta-llama/Llama-2-7b", \
     "--port", "8000", \
     "--gpu-memory-utilization", "0.9", \
     "--max-num-batched-tokens", "10000", \
     "--max-model-len", "4096"]
```

### Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vllm-inference
spec:
  replicas: 2
  template:
    spec:
      containers:
      - name: vllm
        image: my-vllm:latest
        env:
        - name: CUDA_VISIBLE_DEVICES
          value: "0"
        - name: VLLM_ATTENTION_BACKEND
          value: "xformers"  # For faster attention
        resources:
          limits:
            nvidia.com/gpu: 1
            memory: 40Gi
          requests:
            nvidia.com/gpu: 1
            memory: 32Gi
        ports:
        - containerPort: 8000
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          periodSeconds: 30
          failureThreshold: 3
```

### Inference API (OpenAI-compatible)
```bash
# Chat completion
curl http://llm-inference:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "meta-llama/Llama-2-7b",
    "messages": [{"role": "user", "content": "Hello"}],
    "temperature": 0.7,
    "max_tokens": 100
  }'
```

---

## 3. Triton Inference Server (Multi-Model)

**Best for**: Multiple models, ensemble logic, GPU optimization needed

### Directory Structure
```
models/
├── llm/
│   ├── 1/
│   │   └── model.pt
│   └── config.pbtxt
├── embeddings/
│   ├── 1/
│   │   └── model.onnx
│   └── config.pbtxt
└── tokenizer/
    ├── 1/
    │   └── tokenizer.py
    └── config.pbtxt
```

### config.pbtxt (for LLM model)
```pbtxt
name: "llm"
platform: "pytorch_libtorch"
max_batch_size: 4
input [
  {
    name: "input_ids"
    data_type: TYPE_INT64
    dims: [-1]
  }
]
output [
  {
    name: "output"
    data_type: TYPE_FP32
    dims: [-1, 4096]
  }
]
instance_group [
  {
    kind: KIND_GPU
    count: 1
  }
]
```

### Kubernetes StatefulSet
```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: triton-inference
spec:
  serviceName: triton
  replicas: 2
  template:
    spec:
      containers:
      - name: triton
        image: nvcr.io/nvidia/tritonserver:24.02-py3
        ports:
        - containerPort: 8000  # HTTP
        - containerPort: 8001  # gRPC
        volumeMounts:
        - name: model-repo
          mountPath: /models
        env:
        - name: CUDA_VISIBLE_DEVICES
          value: "0"
        resources:
          limits:
            nvidia.com/gpu: 1
            memory: 48Gi
          requests:
            nvidia.com/gpu: 1
            memory: 40Gi
        startupProbe:
          httpGet:
            path: /v2/health/ready
            port: 8000
          failureThreshold: 120
          periodSeconds: 5
      volumes:
      - name: model-repo
        persistentVolumeClaim:
          claimName: triton-models
```

### Client Request (HTTP)
```python
import requests

response = requests.post(
    "http://triton-inference:8000/v2/models/llm/infer",
    json={
        "inputs": [
            {"name": "input_ids", "shape": [1, 10], "datatype": "INT64", "data": [...]}
        ]
    }
)
print(response.json())
```

---

## 4. Ray Serve (Distributed Inference)

**Best for**: Distributed inference, traffic splitting, canary deployments

### app.py
```python
from ray import serve
from transformers import AutoModelForCausalLM

serve.start(detached=True)

@serve.deployment(num_replicas=2)
class LLMDeployment:
    def __init__(self):
        self.model = AutoModelForCausalLM.from_pretrained("mistralai/Mistral-7B")

    async def __call__(self, request):
        prompt = request.query_params.get("prompt")
        output = self.model.generate(prompt)
        return {"text": output}

LLMDeployment.deploy()
```

### Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ray-head
spec:
  replicas: 1
  template:
    spec:
      containers:
      - name: ray
        image: rayproject/ray:latest
        command: ["ray", "start", "--head", "--object-manager-memory=6000000000"]
        ports:
        - containerPort: 6379  # Redis
        - containerPort: 8265  # Dashboard
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ray-worker
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: ray
        image: rayproject/ray:latest
        command: ["ray", "start", "--address=ray-head:6379"]
        resources:
          limits:
            nvidia.com/gpu: 1
          requests:
            nvidia.com/gpu: 1
```

---

## 5. KServe (Enterprise ML Model Serving)

**Best for**: Production ML systems, model versioning, A/B testing, canary rollouts

### InferenceService
```yaml
apiVersion: serving.kserve.io/v1beta1
kind: InferenceService
metadata:
  name: llm-model
  namespace: prod
spec:
  predictor:
    model:
      modelFormat:
        name: pytorch
      storageUri: s3://models/llama-2-7b
      resources:
        limits:
          nvidia.com/gpu: 1
        requests:
          nvidia.com/gpu: 1
      env:
      - name: WORKERS_PER_MODEL
        value: "1"
  canaryTraffic:
    canaryRevisionName: llm-model-v2
    trafficPercent: 10  # 10% traffic to new model
```

### Prediction Request
```bash
curl -X POST http://llm-model.prod.svc.cluster.local:80/v1/models/llm-model:predict \
  -d '{"instances": [{"text": "Hello"}]}'
```

---

## Performance Tuning

### GPU Memory Optimization

**vLLM**:
```bash
# Increase GPU memory utilization
--gpu-memory-utilization 0.95

# Use paged attention for 20% speedup
--enable-prefix-caching

# Use GPTQ quantization for 4x smaller models
--quantization gptq
```

**Triton**:
```yaml
# Dynamic batching for throughput
dynamic_batching {
  preferred_batch_size: [8, 16]
  max_queue_delay_microseconds: 100000  # 100ms
}
```

### Latency vs Throughput

| Framework | P50 Latency | Throughput | Best For |
|-----------|------------|-----------|----------|
| FastAPI | 50-100ms | 100 req/s | Low-latency APIs |
| vLLM | 100-200ms | 500-1000 req/s | Batch/streaming |
| Triton | 20-50ms | 2000+ req/s | High-throughput |
| Ray | 100-300ms | 200-500 req/s | Distributed |
| KServe | 100-200ms | 300-800 req/s | Multi-version |

---

## Choosing an Architecture

```
1. Single model, simple API?
   → FastAPI + Gunicorn

2. Single LLM, high throughput needed?
   → vLLM

3. Multiple models or ensembles?
   → Triton Inference Server

4. Distributed inference, traffic splitting?
   → Ray Serve

5. Production ML system, versioning, canary?
   → KServe

6. Just need to deploy a model?
   → Use model provider (HuggingFace Inference API, Modal, Replicate)
```

---

## References

- vLLM: https://docs.vllm.ai/
- Triton: https://docs.nvidia.com/deeplearning/triton-inference-server/
- Ray Serve: https://docs.ray.io/en/latest/serve/index.html
- KServe: https://kserve.github.io/website/
