# GPU Runtime Configuration for AI Services

## NVIDIA Container Toolkit Installation

### Ubuntu 22.04 LTS (Jammy)

```bash
# Step 1: Add NVIDIA repository
distribution=$(. /etc/os-release;echo $ID$VERSION_ID) \
    && curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | \
       gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
    && curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
       sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
       tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

# Step 2: Install toolkit
apt-get update && apt-get install -y nvidia-container-toolkit

# Step 3: Configure Docker daemon
nvidia-ctk runtime configure --runtime=docker

# Step 4: Restart Docker
systemctl restart docker
```

### Ubuntu 20.04 LTS (Focal)

```bash
curl https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    tee /etc/apt/sources.list.d/nvidia-container-toolkit.list > /dev/null

curl -LsSf https://nvidia.github.io/libnvidia-container/stable/gpg | \
    gpg --dearmor | tee /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg > /dev/null

apt-get update && apt-get install -y nvidia-container-toolkit
nvidia-ctk runtime configure --runtime=docker
systemctl restart docker
```

### Verification

```bash
# Check toolkit installed
nvidia-ctk --version  # Should output: 1.14.0+

# Check Docker knows about nvidia runtime
docker info | grep nvidia

# Test with CUDA image
docker run --rm --gpus all nvidia/cuda:12.0-base nvidia-smi
```

---

## CUDA Version Compatibility Matrix

| NVIDIA Driver | CUDA 12.x | CUDA 11.8 | CUDA 11.7 | Notes |
|---------------|-----------|-----------|-----------|-------|
| **550+** | ✓ (12.4) | ✓ (11.8) | ✗ | Latest, supports Hopper GPUs |
| **535-549** | ✗ | ✓ (11.8) | ✓ (11.7) | LTS for enterprise |
| **525-534** | ✗ | ✓ (11.8) | ✓ (11.7) | Older, not recommended |
| **515-524** | ✗ | ✗ | ✓ (11.7) | End of life |

### Check Your NVIDIA Driver Version

```bash
nvidia-smi | grep "Driver Version"
# Output: Driver Version: 550.120

# Get available CUDA version for this driver
nvidia-smi | grep "CUDA Version"
# Output: CUDA Version: 12.4
```

### Base Image Selection

```yaml
# CUDA 12.0 (Latest, recommended for new projects)
FROM nvidia/cuda:12.0-cudnn8-devel-ubuntu22.04

# CUDA 12.1 (Specific version, PyTorch common)
FROM pytorch/pytorch:2.2.0-cuda12.1-cudnn8-devel

# CUDA 11.8 (Stable, older hardware support)
FROM nvidia/cuda:11.8-cudnn8-devel-ubuntu22.04

# TensorFlow with CUDA
FROM tensorflow/tensorflow:latest-gpu

# Small base images
FROM nvidia/cuda:12.0-runtime-ubuntu22.04  # 2.5GB, runtime only
FROM nvidia/cuda:12.0-devel-ubuntu22.04    # 5GB, with build tools
```

---

## Runtime Configuration in Dockerfile

### Method 1: Using Default Runtime (Modern)

```dockerfile
FROM pytorch/pytorch:2.2.0-cuda12.1-cudnn8-runtime

# This image already has NVIDIA runtime support
# No additional configuration needed

WORKDIR /app
COPY app/ /app/
CMD ["python", "app/main.py"]
```

**Requirement**: Host Docker daemon must have nvidia runtime configured

### Method 2: Explicit Environment Variables

```dockerfile
FROM nvidia/cuda:12.0-devel-ubuntu22.04

ENV PATH=/usr/local/nvidia/bin:${PATH} \
    LD_LIBRARY_PATH=/usr/local/nvidia/lib:/usr/local/nvidia/lib64:${LD_LIBRARY_PATH} \
    CUDA_HOME=/usr/local/cuda \
    NVIDIA_VISIBLE_DEVICES=all \
    NVIDIA_DRIVER_CAPABILITIES=compute,utility

RUN apt-get update && apt-get install -y python3-pip
RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

WORKDIR /app
COPY app/ /app/
CMD ["python", "app/main.py"]
```

### Method 3: docker-compose GPU Configuration

```yaml
version: '3.8'

services:
  inference-service:
    image: my-llm:latest
    runtime: nvidia  # ← Crucial!
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
      - NVIDIA_DRIVER_CAPABILITIES=compute,utility
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
    shm_size: 2gb
    ports:
      - "8000:8000"
```

### Testing GPU Access in Container

```bash
# Test 1: NVIDIA-SMI
docker run --gpus all nvidia/cuda:12.0-base nvidia-smi

# Test 2: PyTorch
docker run --gpus all pytorch/pytorch:2.2.0-cuda12.1-cudnn8-runtime \
    python -c "import torch; print(f'GPU available: {torch.cuda.is_available()}')"

# Test 3: TensorFlow
docker run --gpus all tensorflow/tensorflow:latest-gpu \
    python -c "import tensorflow as tf; print(f'GPUs: {len(tf.config.list_physical_devices(\"GPU\"))}')"

# Test 4: Check CUDA from container
docker run --gpus all my-app python -c \
    "import torch; print(f'CUDA version: {torch.version.cuda}')"
```

---

## Cloud GPU Configuration

### AWS EC2 GPU Instances

**Instance Types:**
```
g4dn    NVIDIA T4 (8-16GB VRAM)      - Recommended for inference
g4ad    AMD GPU                       - Lower cost alternative
g5      NVIDIA L40S (24GB VRAM)      - Recommended for training
p3      NVIDIA A100 (40GB VRAM)      - Large models, distributed training
p4      NVIDIA A100 80GB              - Largest models
```

**Setup Steps:**
```bash
# 1. Launch Ubuntu 22.04 LTS instance with GPU
# 2. SSH into instance

# 3. Install NVIDIA drivers
sudo apt-get update
sudo apt-get install -y nvidia-driver-550-server
sudo reboot

# 4. Verify driver
nvidia-smi

# 5. Install Docker + NVIDIA Container Toolkit
curl https://get.docker.com | sh
sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker

# 6. Test
docker run --rm --gpus all nvidia/cuda:12.0-base nvidia-smi
```

**Dockerfile for AWS:**
```dockerfile
FROM nvidia/cuda:12.0-cudnn8-devel-ubuntu22.04

# Works on g4dn (T4), g5 (L40S), p3 (A100)
# Note: A100 needs special CUDA 12.x for optimal performance

RUN apt-get update && apt-get install -y python3.11 python3-pip
RUN pip install torch torchvision --index-url https://download.pytorch.org/whl/cu120

WORKDIR /app
COPY app/ /app/
CMD ["python", "app/main.py"]
```

### Google Cloud Platform (GCP) Vertex AI / Compute Engine

**Instance Configuration:**
```bash
# gcloud CLI example
gcloud compute instances create my-gpu-vm \
    --machine-type=n1-standard-8 \
    --zone=us-central1-a \
    --image-family=ubuntu-2204-lts \
    --image-project=ubuntu-os-cloud \
    --accelerator=type=nvidia-tesla-t4,count=1

# Install GPU drivers after boot
gcloud compute instances list  # Get instance name
gcloud compute ssh my-gpu-vm

# Then same steps as AWS
sudo apt-get install -y nvidia-driver-550-server
sudo reboot
```

**Dockerfile for GCP:**
```dockerfile
# Same as AWS, CUDA compatibility applies
FROM pytorch/pytorch:2.2.0-cuda12.1-cudnn8-devel

# T4 (8GB), A100 (40GB), L4 (24GB) all supported
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app/ /app/
CMD ["python", "app/main.py"]
```

### Azure Machine Learning

**Container Registry + GPU Compute:**
```bash
# Create GPU compute
az ml compute create \
    --name gpu-cluster \
    --type AmlCompute \
    --min-instances 0 \
    --max-instances 4 \
    --vm-size Standard_NC6s_v3  # 1x Tesla V100

# Push image to ACR
az acr build --registry <your-acr> --image my-llm:latest .

# Deploy as job
az ml job create -f job.yml
```

**job.yml:**
```yaml
$schema: https://azuremlschemas.blob.core.windows.net/latest/job.schema.json
type: command

compute: azureml:gpu-cluster

environment:
  image: <your-acr>.azurecr.io/my-llm:latest

command: python app/main.py

resources:
  gpu_count: 1
```

---

## GPU Memory Management

### Out of Memory (OOM) Prevention

```python
# In your training/inference script
import torch
import os

# Set memory fraction to prevent full allocation
os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'max_split_size_mb=512'

# Explicit memory clearing
def inference_batch(model, batch):
    with torch.no_grad():
        output = model(batch)

    torch.cuda.empty_cache()  # Clear after batch
    return output

# Monitor memory during training
torch.cuda.reset_peak_memory_stats()
```

### Dockerfile with Memory Tuning

```dockerfile
FROM pytorch/pytorch:2.2.0-cuda12.1-cudnn8-devel

ENV PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512 \
    CUDA_VISIBLE_DEVICES=0 \
    TORCH_NUM_THREADS=8

WORKDIR /app
COPY app/ /app/
ENTRYPOINT ["python", "app/main.py"]
```

### Monitoring GPU Memory

```bash
# Real-time GPU memory monitoring
watch -n 1 nvidia-smi --query-gpu=index,name,utilization.gpu,utilization.memory,memory.used,memory.free --format=csv,noheader

# Per-process memory
nvidia-smi --query-compute-apps=pid,process_name,gpu_memory_usage --format=csv,noheader | sort -k3 -rn

# Inside container
docker run --gpus all --rm my-app python -c \
    "import torch; print(f'Allocated: {torch.cuda.memory_allocated() / 1e9:.2f}GB')"
```

---

## Advanced: GPU Time-Slicing and MIG

### Time-Slicing (Share single GPU across jobs)

**Requires nvidia-k8s-device-plugin 0.12.0+**

```yaml
# /etc/nvidia-container-runtime/config.toml
[nvidia-container-runtime]
mode = "auto"
nvidia-smi-path = "/usr/bin/nvidia-smi"
ldcache = ""
ldconfig = "@/sbin/ldconfig.real"  # For WSL2
```

**In docker-compose:**
```yaml
services:
  job-1:
    image: my-llm:latest
    runtime: nvidia
    environment:
      - NVIDIA_VISIBLE_DEVICES=GPU-12345678  # Specific GPU UUID
      - CUDA_MPS_PIPE_DIRECTORY=/tmp/nvidia-mps

  job-2:
    image: my-llm:latest
    runtime: nvidia
    environment:
      - NVIDIA_VISIBLE_DEVICES=GPU-12345678  # Same GPU, different MPS pipe
      - CUDA_MPS_PIPE_DIRECTORY=/tmp/nvidia-mps-2
```

### MIG (Multi-Instance GPU) - A100 only

```bash
# List MIG profiles
nvidia-smi -L | grep MIG

# Enable MIG mode (requires GPU reset)
sudo nvidia-smi -mig 1

# Create MIG instance
sudo nvidia-smi mig -cgi 9,9,9 -C

# Check instances
nvidia-smi mig -lgi
```

**Docker with MIG:**
```dockerfile
FROM nvidia/cuda:12.0-devel-ubuntu22.04

ENV NVIDIA_VISIBLE_DEVICES=MIG-GPU-12345678/1/0  # Specific MIG instance

RUN apt-get install -y python3-pip
RUN pip install torch

WORKDIR /app
COPY app/ /app/
CMD ["python", "app/main.py"]
```

---

## Troubleshooting GPU Issues

### GPU Not Detected

```bash
# Check 1: Driver installed
nvidia-smi
# If fails: Install drivers for your distro

# Check 2: NVIDIA Container Toolkit
docker info | grep nvidia
# If missing: apt install nvidia-container-toolkit

# Check 3: Docker daemon has nvidia-cdi-hook
systemctl status docker
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker

# Check 4: Runtime priority
cat /etc/docker/daemon.json
# Should have: "runtimes": { "nvidia": {...} }
```

### CUDA Version Mismatch

```bash
# Check container CUDA
docker run --rm my-app nvcc --version

# Compare with driver
nvidia-smi | grep "CUDA Version"

# If mismatch, update Dockerfile FROM image
# e.g., pytorch/pytorch:2.2.0-cuda12.1-cudnn8-devel matches CUDA 12.1
```

### Memory Access Errors

```bash
# Symptom: "CUDA out of memory" or "Invalid resource handle"
# Solution: Reduce batch size or enable memory optimizations

# In Dockerfile or env
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb=512
export CUDA_LAUNCH_BLOCKING=1  # Synchronous errors (slower but clearer)

# Test
docker run --gpus all \
    -e CUDA_LAUNCH_BLOCKING=1 \
    -e PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb=512 \
    my-app python app/main.py
```

### GPU Utilization Low (<50%)

```bash
# Check if I/O bound
docker stats --no-stream my-app  # CPU > GPU utilization

# Solutions:
# 1. Increase batch size
# 2. Use multiple workers (DataLoader workers)
# 3. Check if using correct device (verify torch.cuda.is_available() = True)
# 4. Profile with: python -m cProfile -s cumtime app/main.py
```

---

## Reference

**NVIDIA Docker**: https://github.com/NVIDIA/nvidia-docker
**NVIDIA Container Toolkit**: https://docs.nvidia.com/container-toolkit/
**CUDA Compatibility**: https://docs.nvidia.com/cuda/cuda-toolkit-release-notes/
**Driver Download**: https://www.nvidia.com/Download/driverDetails.aspx
