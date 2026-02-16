# AI Inference Patterns: Triton, TorchServe, vLLM, TGI

## Pattern 1: vLLM (High-Throughput LLM Serving)

**Best for**: Chat APIs, high-throughput inference, real-time generation

**Dockerfile:**
```dockerfile
FROM nvidia/cuda:12.0-devel-ubuntu22.04

WORKDIR /app

RUN pip install vllm transformers

EXPOSE 8000

# Auto-configures tensor parallelism, scheduling, KV cache optimization
CMD ["python", "-m", "vllm.entrypoints.openai.api_server", \
     "--model", "meta-llama/Llama-2-70b-chat-hf", \
     "--dtype", "float16", \
     "--max-model-len", "4096", \
     "--tensor-parallel-size", "4"]
```

**Key Features**:
- **Continuous batching**: Packs requests from multiple clients into single batch
- **Paged attention**: Efficient KV cache management (20-30% speedup)
- **Speculative decoding**: Speed up token generation with speculative tokens

**Example API Call:**
```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "meta-llama/Llama-2-70b-chat-hf",
    "messages": [{"role": "user", "content": "Hello!"}],
    "temperature": 0.7
  }'
```

**Performance Benchmark (Llama 2 70B, 8x A100 80GB)**:
- Throughput: 1000+ tokens/second
- Latency: 50-100ms per token (chat mode)
- Capacity: 32 concurrent users

---

## Pattern 2: Text Generation Inference (TGI) - Hugging Face

**Best for**: Optimized inference for Hugging Face models, fine-grained control

**Dockerfile:**
```dockerfile
FROM ghcr.io/huggingface/text-generation-inference:2.0-gpu

ENV MODEL_ID=meta-llama/Llama-2-7b-chat-hf \
    QUANTIZE=bitsandbytes

# TGI auto-handles model download, quantization, optimization
CMD ["--port", "8000"]
```

**Supported Quantizations:**
```dockerfile
# GPTQ
ENV QUANTIZE=gptq

# AWQ
ENV QUANTIZE=awq

# bitsandbytes (8-bit)
ENV QUANTIZE=bitsandbytes
```

**Features**:
- **Token streaming**: Stream tokens as generated
- **Adaptive batching**: Groups requests with similar sequence lengths
- **Optimized kernels**: Flash attention, paged attention built-in

**Example:**
```bash
curl http://localhost:8000/generate_stream \
  -X POST \
  -d '{"inputs":"What is machine learning?"}' \
  -H 'Content-Type: application/json'
```

---

## Pattern 3: Triton Inference Server (Multi-Model)

**Best for**: Deploying multiple models, ensemble models, feature engineering pipelines

**Dockerfile:**
```dockerfile
FROM nvcr.io/nvidia/tritonserver:24.02-py3

WORKDIR /models

# Download models
RUN wget -O bert.tar.gz \
  https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/resolve/main/pytorch_model.bin

# Copy model config
COPY ./model_repository /models

EXPOSE 8000 8001 8002

# REST on 8000, gRPC on 8001, metrics on 8002
CMD ["tritonserver", "--model-repository=/models"]
```

**Model Configuration (model_repository/bert/config.pbtxt):**
```protobuf
name: "bert"
platform: "pytorch_libtorch"
max_batch_size: 32

input [
  {
    name: "input_ids"
    data_type: TYPE_INT64
    dims: [-1]
  }
]

output [
  {
    name: "embeddings"
    data_type: TYPE_FP32
    dims: [-1, 384]
  }
]

instance_group [
  {
    kind: KIND_GPU
    gpus: [0]
  }
]
```

**Features**:
- **Ensemble**: Chain multiple models (e.g., preprocessing → inference → postprocessing)
- **Dynamic batching**: Automatically batch requests
- **Metrics**: Prometheus metrics on port 8002

---

## Pattern 4: TorchServe (PyTorch Model Serving)

**Best for**: PyTorch models, custom serving logic, A/B testing

**Dockerfile:**
```dockerfile
FROM pytorch/pytorch:2.0-cuda11.8-cudnn8-devel

WORKDIR /app

RUN pip install torchserve torch-model-archiver torch-workflow-archiver

# Create model archive (.mar file)
RUN torch-model-archiver \
  --model-name ResNet50 \
  --version 1.0 \
  --model-file model.py \
  --serialized-file resnet50-11577d5f.pth \
  --handler image_classifier \
  --export-path model-store

EXPOSE 8080 8081

CMD ["torchserve", \
     "--start", \
     "--model-store", "model-store", \
     "--models", "ResNet50=ResNet50.mar"]
```

**Custom Handler (handler.py):**
```python
import torch
from ts.torch_handler.base_handler import BaseHandler

class ImageClassifier(BaseHandler):
    def __init__(self):
        super().__init__()
        self.model = None
        self.initialized = False

    def initialize(self, context):
        # Load model
        self.model = torch.jit.load(self.manifest['model']['serializedFile'])
        self.initialized = True

    def preprocess(self, data):
        # Image preprocessing
        image = data[0]['body']  # PIL Image
        return image.convert('RGB')

    def inference(self, processed_input):
        # Forward pass
        with torch.no_grad():
            output = self.model(processed_input)
        return output

    def postprocess(self, inference_output):
        # Return top-5 predictions
        top5 = torch.topk(inference_output, 5)
        return [{"class": idx.item(), "score": score.item()} for idx, score in zip(*top5)]
```

---

## Pattern 5: Ray Serve (Distributed, Scalable Inference)

**Best for**: Complex pipelines, multiple models with different resources, auto-scaling

**Dockerfile:**
```dockerfile
FROM rayproject/ray:latest-gpu

WORKDIR /app

RUN pip install "ray[serve]" transformers torch

COPY app.py /app/

CMD ["python", "app.py"]
```

**app.py:**
```python
from ray import serve
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

serve.start(detached=True)

class LLMModel:
    def __init__(self, model_id="meta-llama/Llama-2-7b-chat-hf"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_id,
            device_map="auto",
            torch_dtype=torch.float16
        )

    async def __call__(self, prompt: str) -> str:
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        outputs = self.model.generate(**inputs, max_new_tokens=100)
        return self.tokenizer.decode(outputs[0])

# Deploy with auto-scaling
serve.run(LLMModel.bind("meta-llama/Llama-2-7b-chat-hf"),
         route_prefix="/llm",
         num_replicas=4)  # Auto-scale between 1-4 replicas
```

**Features**:
- **Auto-scaling**: Scale based on queue depth
- **Request routing**: Smart routing based on model capacity
- **Canary deployments**: Route % of traffic to new version

---

## Pattern 6: FastAPI + uvicorn (Custom Inference Server)

**Best for**: Custom preprocessing, multi-step inference, RAG pipelines

**Dockerfile:**
```dockerfile
FROM pytorch/pytorch:2.2.0-cuda12.1-cudnn8-runtime

WORKDIR /app

RUN pip install fastapi uvicorn transformers

COPY app.py /app/

HEALTHCHECK --interval=10s --timeout=5s --start-period=60s \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

**app.py:**
```python
from fastapi import FastAPI, BackgroundTasks
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

app = FastAPI()

# Load model at startup
model = None
tokenizer = None

@app.on_event("startup")
async def load_model():
    global model, tokenizer
    model = AutoModelForCausalLM.from_pretrained(
        "meta-llama/Llama-2-7b-chat-hf",
        device_map="auto",
        torch_dtype=torch.float16
    )
    tokenizer = AutoTokenizer.from_pretrained(
        "meta-llama/Llama-2-7b-chat-hf"
    )

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/generate")
async def generate(prompt: str, max_tokens: int = 100):
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    with torch.no_grad():
        outputs = model.generate(**inputs, max_new_tokens=max_tokens)
    return {"result": tokenizer.decode(outputs[0])}

# Streaming endpoint
@app.post("/generate_stream")
async def generate_stream(prompt: str):
    from fastapi.responses import StreamingResponse

    async def generate_tokens():
        # Implement token-by-token streaming
        pass

    return StreamingResponse(generate_tokens(), media_type="text/event-stream")
```

---

## Comparison Table

| Framework | Throughput | Latency | Model Support | Ease of Use |
|-----------|-----------|---------|---------------|------------|
| **vLLM** | Excellent | Excellent | LLM-optimized | Easy |
| **TGI** | Excellent | Excellent | HF models | Easy |
| **Triton** | Good | Good | Multi-model | Medium |
| **TorchServe** | Good | Medium | PyTorch | Medium |
| **Ray Serve** | Good | Good | Any Python | Hard |
| **FastAPI** | Baseline | Baseline | Any | Easy |

---

## Performance Tuning for Each Pattern

### vLLM Tuning
```bash
# Increase throughput
docker run -it --gpus all \
  --shm-size=20g \
  vllm python -m vllm.entrypoints.openai.api_server \
  --model meta-llama/Llama-2-70b-chat-hf \
  --max-num-seqs 256 \
  --max-seq-len-to-capture 4096 \
  --gpu-memory-utilization 0.95
```

### TGI Tuning
```dockerfile
ENV SAFETENSORS_FAST_GPU=1 \
    FLASH_ATTENTION=true \
    MAX_BATCH_PREFILL_TOKENS=4096 \
    BATCH_SAFETY_MARGIN=0.9
```

### Triton Dynamic Batching
```protobuf
dynamic_batching {
  preferred_batch_size: [16, 32]
  max_queue_delay_microseconds: 1000
  preserve_ordering: true
}
```

---

## Reference

- **vLLM**: https://docs.vllm.ai/
- **TGI**: https://huggingface.co/docs/text-generation-inference/
- **Triton**: https://github.com/triton-inference-server/server
- **TorchServe**: https://pytorch.org/serve/
- **Ray Serve**: https://docs.ray.io/en/latest/serve/
