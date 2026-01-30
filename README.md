# 🚀 Optimum CLI Pro

> **Production-grade CLI tool for optimizing any HuggingFace model with multiple acceleration backends**

A comprehensive solution for model optimization, benchmarking, registry management, A/B testing, and production serving with a beautiful web interface.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

---

## 📑 Table of Contents

- [Features](#-features)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Supported Tasks](#-supported-tasks)
- [CLI Commands](#-cli-commands)
- [Configuration](#-configuration)
- [REST API](#-rest-api)
- [Web Interface](#-web-interface)
- [Model Registry](#-model-registry)
- [A/B Testing](#-ab-testing)
- [Architecture](#-architecture)
- [Examples](#-examples)
- [Development](#-development)
- [Deployment](#-deployment)
- [Troubleshooting](#-troubleshooting)

---

## ✨ Features

### 🎯 **Model Optimization**
- **4 Acceleration Backends**: ONNX Runtime, OpenVINO, BetterTransformer, Auto-detection
- **Automatic Task Detection**: Infers task type from model architecture
- **Quantization Support**: INT8 quantization for 2-4x size reduction
- **Custom Optimization**: Configure batch size, sequence length, and more
- **Universal Support**: Works with 100+ HuggingFace models (BERT, GPT, ViT, etc.)

### 📦 **Model Registry**
- **SQLite-Based Registry**: Persistent storage for optimized models
- **Version Control**: Track multiple versions of the same model
- **Metadata Management**: Store optimization settings, metrics, tags, and descriptions
- **Easy Discovery**: List, search, and inspect registered models
- **Async Operations**: High-performance database queries

### 🧪 **A/B Testing**
- **Side-by-Side Comparison**: Compare optimized models against each other
- **Performance Metrics**: Throughput (req/s), latency, memory usage, model size
- **Statistical Analysis**: Automatic speedup calculation and winner detection
- **Test History**: Track all A/B test results with timestamps
- **CLI & API Support**: Run tests from command line or REST API

### 🌐 **REST API & Web Interface**
- **FastAPI Server**: High-performance async API with OpenAPI documentation
- **Beautiful Custom UI**: Gradient-themed web interface (no Swagger!)
- **Real-Time Inference**: Test models directly from the browser
- **Visual Comparisons**: Interactive A/B testing dashboard with metrics
- **Model Management**: Browse and manage registry via intuitive UI
- **Server Status**: Real-time health monitoring

### 📈 **MLOps Integration**
- **MLflow Support**: Track experiments, models, and metrics
- **Weights & Biases**: Log optimization results and compare runs
- **Cost Tracking**: Monitor optimization time and resource usage

### 🚀 **Production Ready**
- **Docker Support**: Containerized deployment with docker-compose
- **AWS CloudFormation**: One-click infrastructure setup for cloud deployment
- **Health Checks**: Built-in monitoring endpoints (`/health`, `/api/v1/health`)
- **Async Operations**: High concurrency support with aiosqlite
- **Error Handling**: Comprehensive error messages and logging

---

## 📥 Installation

### Prerequisites

- **Python**: 3.10 or higher
- **pip**: 21.0 or higher
- **OS**: Windows, Linux, or macOS
- **(Optional)** Intel CPU for OpenVINO optimization

### Install from Source

```bash
# Clone the repository
git clone https://github.com/yourusername/optimum-cli-pro.git
cd optimum-cli-pro

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install the package
pip install -e .
```

### Install with Optional Dependencies

```bash
# Install with all backends and MLOps tools
pip install -e ".[all]"

# Install with specific backends only
pip install -e ".[onnx]"      # ONNX Runtime only
pip install -e ".[openvino]"  # OpenVINO only
pip install -e ".[mlops]"     # MLflow + Weights & Biases
```

### Verify Installation

```bash
optimum-pro --help
```

You should see:

```
 Usage: optimum-pro [OPTIONS] COMMAND [ARGS]...

╭─ Commands ───────────────────────────────────────────╮
│ optimize   Optimize a HuggingFace model             │
│ registry   Model registry management                │
│ serve      Start API server                         │
╰──────────────────────────────────────────────────────╯
```

---

## 🚀 Quick Start

### 1. Optimize Your First Model

```bash
# Optimize BERT with ONNX backend (recommended for cross-platform)
optimum-pro optimize model bert-base-uncased --backend onnx

# Let the CLI choose the best backend for your hardware
optimum-pro optimize model bert-base-uncased --backend auto

# Optimize with OpenVINO (fastest on Intel CPUs)
optimum-pro optimize model bert-base-uncased --backend openvino

# Optimize with custom settings
optimum-pro optimize model roberta-large \
  --backend onnx \
  --batch-size 8 \
  --sequence-length 512 \
  --quantization \
  --output ./my_models
```

**Output Example:**
```
🔍 Loading model bert-base-uncased...
✅ Model loaded successfully
🎯 Task detected: fill-mask
🚀 Optimizing with ONNX backend...
⏱️  Optimization time: 19.23s
📊 Model size: 418.92 MB
✅ Model saved to: ./optimized_models/bert-base-uncased
```

### 2. Register Your Model

```bash
# Register the optimized model in the registry
optimum-pro registry push \
  --name "bert-opt-v1" \
  --path "./optimized_models/bert-base-uncased" \
  --backend onnx \
  --version "1.0.0" \
  --description "BERT base optimized with ONNX Runtime and INT8 quantization"

# List all registered models
optimum-pro registry list
```

**Output Example:**
```
╭─────────────────────── Registered Models ───────────────────────╮
│ Name          Version  Backend    Size        Created            │
├─────────────────────────────────────────────────────────────────┤
│ bert-opt-v1   1.0.0    onnx      418.92 MB   2026-01-30 10:30  │
╰─────────────────────────────────────────────────────────────────╯
```

### 3. Test Your Model

```bash
# Get model information and run a test inference
optimum-pro registry info bert-opt-v1 --test --input "Paris is the capital of [MASK]."
```

**Output Example:**
```
📦 Model: bert-opt-v1
🏷️  Version: 1.0.0
⚙️  Backend: onnx
📊 Size: 418.92 MB
🎯 Task: fill-mask
📝 Description: BERT base optimized with ONNX Runtime

🧪 Test Inference:
Input: "Paris is the capital of [MASK]."
Output: france (score: 0.9821)
```

### 4. Optimize Another Model for Comparison

```bash
# Optimize with a different backend
optimum-pro optimize model bert-base-uncased --backend openvino

# Register the second version
optimum-pro registry push \
  --name "bert-opt-v2" \
  --path "./optimized_models/bert-base-uncased" \
  --backend openvino \
  --version "1.0.0" \
  --description "BERT base optimized with OpenVINO"
```

### 5. Run A/B Testing

```bash
# Create an A/B test to compare both models
optimum-pro registry ab-test \
  --name "onnx-vs-openvino" \
  --model-a bert-opt-v1 \
  --model-b bert-opt-v2 \
  --description "ONNX vs OpenVINO performance comparison"

# Run the comparison with 100 iterations
optimum-pro registry ab-compare onnx-vs-openvino \
  --input "The capital of France is [MASK]." \
  --iterations 100

# View all A/B test results
optimum-pro registry ab-list
```

**Output Example:**
```
🧪 A/B Test Results: onnx-vs-openvino
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Model A (bert-opt-v1):
  Throughput: 46.44 requests/sec
  Latency: 21.53 ms
  Size: 508.29 MB

Model B (bert-opt-v2):
  Throughput: 43.36 requests/sec
  Latency: 23.07 ms
  Size: 418.92 MB

🏆 Winner: Model A (bert-opt-v1)
📊 Speedup: 1.07x faster
💾 Size Difference: Model B is 89.37 MB smaller
```

### 6. Start the Web Server

```bash
# Start the API server with web interface
optimum-pro serve start --port 8000 --host 0.0.0.0

# Server runs at: http://localhost:8000
```

**Access the Web Interface:**

Open your browser and navigate to `http://localhost:8000` to access:
- 📊 **Models Tab**: Browse all registered models
- 🎯 **Inference Tab**: Test models with custom inputs
- 🧪 **A/B Testing Tab**: Run and visualize model comparisons

---

## 🎯 Supported Tasks

Optimum CLI Pro supports **9+ task types** across text, vision, and multimodal domains:

### 📝 Text Tasks

| Task | Description | Example Models | Example Use Case |
|------|-------------|----------------|------------------|
| **fill-mask** | Predict masked tokens in text | BERT, RoBERTa, DistilBERT, ALBERT | "Paris is the capital of [MASK]" → "france" |
| **text-classification** | Classify text into categories | BERT, RoBERTa, DistilBERT | "This movie is amazing!" → positive |
| **token-classification** | Label each token (NER, POS) | BERT, RoBERTa, DistilBERT | "John lives in Paris" → John=PERSON, Paris=LOCATION |
| **text-generation** | Generate text from prompts | GPT-2, GPT-Neo, GPT-J, LLaMA | "Once upon a time" → complete story |
| **question-answering** | Extract answers from context | BERT, RoBERTa, ALBERT, DistilBERT | Context + "Who is the president?" → answer |

### 🖼️ Vision Tasks

| Task | Description | Example Models | Example Use Case |
|------|-------------|----------------|------------------|
| **image-classification** | Classify images into categories | ViT, ResNet, EfficientNet, ConvNeXt | Image → "cat", "dog", "car" |
| **object-detection** | Detect and locate objects | YOLO, DETR, Faster R-CNN | Find all people and cars in image |
| **image-segmentation** | Segment image into regions | SegFormer, Mask R-CNN, UNet | Separate foreground from background |

### 🔀 Multimodal Tasks

| Task | Description | Example Models | Example Use Case |
|------|-------------|----------------|------------------|
| **zero-shot-image-classification** | Classify images without training | CLIP, ALIGN | Classify images with custom labels |

> **💡 Pro Tip**: Tasks are automatically detected from model architecture. You don't need to specify `--task` unless you want to override the auto-detection.

---

## 🛠️ CLI Commands

### Main Command Groups

```bash
optimum-pro [OPTIONS] COMMAND [ARGS]...
```

**Available Commands:**
- `optimize` - Optimize HuggingFace models
- `registry` - Manage model registry
- `serve` - Start REST API server

---

### `optimize model` - Model Optimization

Optimize any HuggingFace model with various backends and configurations.

```bash
optimum-pro optimize model <MODEL_ID> [OPTIONS]
```

#### Required Arguments

| Argument | Description |
|----------|-------------|
| `MODEL_ID` | HuggingFace model ID (e.g., `bert-base-uncased`) or local path |

#### Options

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--backend` | `-b` | choice | `auto` | Backend to use: `auto`, `onnx`, `openvino`, `bettertransformer` |
| `--output` | `-o` | path | `./optimized_models` | Output directory for optimized model |
| `--task` | `-t` | str | auto-detect | Task type (see [Supported Tasks](#-supported-tasks)) |
| `--batch-size` | | int | 1 | Batch size for optimization |
| `--sequence-length` | | int | 128 | Maximum sequence length (for text models) |
| `--quantization` | | flag | enabled | Enable INT8 quantization (default: ON) |
| `--no-quantization` | | flag | | Disable quantization |
| `--track-mlflow` | | flag | | Enable MLflow experiment tracking |
| `--track-wandb` | | flag | | Enable Weights & Biases tracking |

#### Backend Comparison

| Backend | Best For | Speed | Size | Compatibility |
|---------|----------|-------|------|---------------|
| **auto** | Automatic selection | - | - | Detects best backend for your hardware |
| **onnx** | Cross-platform deployment | ⚡⚡⚡ Fast | 📦 Medium | Works everywhere (CPU/GPU) |
| **openvino** | Intel CPUs | ⚡⚡⚡⚡ Fastest | 📦📦 Small | Intel CPUs only |
| **bettertransformer** | Native PyTorch | ⚡⚡ Medium | 📦📦📦 Large | PyTorch environments |

#### Examples

```bash
# Basic optimization with auto backend
optimum-pro optimize model bert-base-uncased --backend auto

# Optimize GPT-2 for text generation
optimum-pro optimize model gpt2 --backend onnx --task text-generation

# Optimize ViT for image classification with custom settings
optimum-pro optimize model google/vit-base-patch16-224 \
  --backend openvino \
  --batch-size 16 \
  --no-quantization

# Optimize with MLflow tracking
optimum-pro optimize model roberta-large \
  --backend onnx \
  --quantization \
  --track-mlflow

# Optimize and save to custom directory
optimum-pro optimize model distilbert-base-uncased \
  --backend onnx \
  --output ./my_models/distilbert
```

---

### `registry` - Model Registry Management

Manage optimized models in a persistent SQLite registry.

#### Subcommands

```bash
optimum-pro registry [SUBCOMMAND] [OPTIONS]
```

---

#### `registry push` - Register a Model

Add an optimized model to the registry.

```bash
optimum-pro registry push [OPTIONS]
```

**Options:**

| Option | Short | Type | Required | Description |
|--------|-------|------|----------|-------------|
| `--name` | `-n` | str | ✅ | Unique model name |
| `--path` | `-p` | path | ✅ | Path to optimized model directory |
| `--backend` | `-b` | str | ✅ | Backend used: `onnx`, `openvino`, `bettertransformer` |
| `--version` | `-v` | str | | Model version (default: `1.0.0`) |
| `--description` | `-d` | str | | Model description |
| `--tags` | `-t` | str | | Comma-separated tags |

**Example:**

```bash
optimum-pro registry push \
  --name "bert-qa-prod" \
  --path "./optimized_models/bert-large-uncased-whole-word-masking-finetuned-squad" \
  --backend onnx \
  --version "2.1.0" \
  --description "Production BERT for Q&A with INT8 quantization" \
  --tags "qa,production,quantized"
```

---

#### `registry list` - List All Models

Display all registered models.

```bash
optimum-pro registry list
```

**Example Output:**

```
╭──────────────────────────── Registered Models ────────────────────────────╮
│ Name           Version  Backend    Size        Task          Created       │
├───────────────────────────────────────────────────────────────────────────┤
│ bert-opt-v1    1.0.0    onnx      418.92 MB   fill-mask    2026-01-30    │
│ bert-opt-v2    1.0.0    openvino  508.29 MB   fill-mask    2026-01-30    │
│ gpt2-gen       1.0.0    onnx      548.12 MB   generation   2026-01-29    │
╰───────────────────────────────────────────────────────────────────────────╯
```

---

#### `registry info` - Get Model Details

Display detailed information about a specific model.

```bash
optimum-pro registry info <MODEL_NAME> [OPTIONS]
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `MODEL_NAME` | Name of the registered model |

**Options:**

| Option | Description |
|--------|-------------|
| `--test` | Run a test inference |
| `--input` | Test input text (requires `--test`) |

**Example:**

```bash
optimum-pro registry info bert-opt-v1 --test --input "Machine learning is [MASK]."
```

**Example Output:**

```
╭───────────────── Model Information ─────────────────╮
│ Name:        bert-opt-v1                            │
│ Version:     1.0.0                                  │
│ Backend:     onnx                                   │
│ Task:        fill-mask                              │
│ Size:        418.92 MB                              │
│ Created:     2026-01-30 10:30:45                    │
│ Description: BERT base optimized with ONNX Runtime  │
│ Tags:        bert, fill-mask, onnx                  │
╰─────────────────────────────────────────────────────╯

🧪 Test Inference:
Input: "Machine learning is [MASK]."
Predictions:
  1. used      (score: 0.1234)
  2. important (score: 0.0987)
  3. popular   (score: 0.0765)
```

---

#### `registry ab-test` - Create A/B Test

Create a new A/B test to compare two models.

```bash
optimum-pro registry ab-test [OPTIONS]
```

**Options:**

| Option | Short | Type | Required | Description |
|--------|-------|------|----------|-------------|
| `--name` | `-n` | str | ✅ | Unique test name |
| `--model-a` | `-a` | str | ✅ | First model name |
| `--model-b` | `-b` | str | ✅ | Second model name |
| `--description` | `-d` | str | | Test description |

**Example:**

```bash
optimum-pro registry ab-test \
  --name "onnx-vs-openvino-bert" \
  --model-a bert-opt-v1 \
  --model-b bert-opt-v2 \
  --description "Compare ONNX vs OpenVINO on BERT base"
```

---

#### `registry ab-compare` - Run A/B Test

Execute an A/B test and measure performance metrics.

```bash
optimum-pro registry ab-compare <TEST_NAME> [OPTIONS]
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `TEST_NAME` | Name of the A/B test |

**Options:**

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--input` | `-i` | str | required | Input text for testing |
| `--iterations` | `-n` | int | 100 | Number of iterations to run |

**Example:**

```bash
optimum-pro registry ab-compare onnx-vs-openvino-bert \
  --input "The quick brown [MASK] jumps over the lazy dog." \
  --iterations 200
```

**Example Output:**

```
🧪 Running A/B Test: onnx-vs-openvino-bert
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Testing Model A (bert-opt-v1)...
Progress: ████████████████████ 100% (200/200)

Testing Model B (bert-opt-v2)...
Progress: ████████████████████ 100% (200/200)

📊 Results:
╭──────────────────────────────────────────────────────╮
│ Metric          Model A      Model B      Winner     │
├──────────────────────────────────────────────────────┤
│ Throughput      46.44 req/s  43.36 req/s  Model A    │
│ Avg Latency     21.53 ms     23.07 ms     Model A    │
│ Model Size      508.29 MB    418.92 MB    Model B    │
│ Memory Usage    1.2 GB       1.0 GB       Model B    │
╰──────────────────────────────────────────────────────╯

🏆 Overall Winner: Model A (bert-opt-v1)
📈 Speedup: 1.07x faster
💾 Size Trade-off: 89.37 MB larger
```

---

#### `registry ab-list` - List All A/B Tests

Display all A/B tests and their results.

```bash
optimum-pro registry ab-list
```

**Example Output:**

```
╭────────────────────── A/B Test History ──────────────────────╮
│ Test Name              Models               Status  Winner    │
├──────────────────────────────────────────────────────────────┤
│ onnx-vs-openvino-bert  bert-v1 vs bert-v2  ✅ Done  bert-v1  │
│ quantized-comparison   bert-q8 vs bert-fp32 ✅ Done bert-q8  │
│ gpt-backends           gpt-onnx vs gpt-ov   ✅ Done gpt-onnx │
╰──────────────────────────────────────────────────────────────╯
```

---

### `serve` - Start API Server

Start the FastAPI server with web interface.

#### Subcommands

---

#### `serve start` - Start Server

Launch the REST API server with web UI.

```bash
optimum-pro serve start [OPTIONS]
```

**Options:**

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--host` | `-h` | str | `0.0.0.0` | Host to bind to |
| `--port` | `-p` | int | `8000` | Port to listen on |
| `--reload` | | flag | | Enable auto-reload (development) |
| `--workers` | `-w` | int | 1 | Number of worker processes |

**Examples:**

```bash
# Start server on default port (8000)
optimum-pro serve start

# Start on custom port with auto-reload (development)
optimum-pro serve start --port 3000 --reload

# Production server with multiple workers
optimum-pro serve start --host 0.0.0.0 --port 8000 --workers 4
```

**Server Endpoints:**
- `http://localhost:8000` - Web Interface
- `http://localhost:8000/docs` - API Documentation (Swagger UI)
- `http://localhost:8000/redoc` - Alternative API Docs
- `http://localhost:8000/health` - Health Check

---

#### `serve stop` - Stop Server

Stop the running API server.

```bash
optimum-pro serve stop
```

---

#### `serve status` - Server Status

Check if the server is running.

```bash
optimum-pro serve status
```

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=1

# Model Registry
REGISTRY_DB_PATH=./data/registry.db

# Model Storage
MODELS_DIR=./optimized_models

# MLflow Configuration
MLFLOW_TRACKING_URI=http://localhost:5000
MLFLOW_EXPERIMENT_NAME=optimum-cli

# Weights & Biases
WANDB_PROJECT=optimum-cli
WANDB_ENTITY=your-username

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/optimum-cli.log

# Optimization Defaults
DEFAULT_BACKEND=auto
DEFAULT_BATCH_SIZE=1
DEFAULT_SEQUENCE_LENGTH=128
ENABLE_QUANTIZATION=true
```

### Configuration File

Create `config.yaml`:

```yaml
# config.yaml
api:
  host: "0.0.0.0"
  port: 8000
  workers: 4
  cors_origins:
    - "http://localhost:3000"
    - "https://yourdomain.com"

registry:
  db_path: "./data/registry.db"
  backup_enabled: true
  backup_interval: "24h"

optimization:
  default_backend: "auto"
  default_batch_size: 1
  default_sequence_length: 128
  quantization_enabled: true
  
  backends:
    onnx:
      enabled: true
      optimization_level: 99
    openvino:
      enabled: true
      device: "CPU"
    bettertransformer:
      enabled: true

mlops:
  mlflow:
    enabled: false
    tracking_uri: "http://localhost:5000"
    experiment_name: "optimum-cli"
  
  wandb:
    enabled: false
    project: "optimum-cli"
    entity: "your-username"

logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: "./logs/optimum-cli.log"
  rotation: "10 MB"
```

---

## 🌐 REST API

### Base URL

```
http://localhost:8000/api/v1
```

### Authentication

Currently, the API is open (no authentication required). For production, implement JWT or API key authentication.

---

### Endpoints

#### Health Check

```http
GET /health
GET /api/v1/health
```

**Response:**

```json
{
  "status": "healthy",
  "timestamp": "2026-01-30T10:30:00Z",
  "version": "1.0.0"
}
```

---

#### List Models

Get all registered models.

```http
GET /api/v1/registry/models
```

**Response:**

```json
{
  "models": [
    {
      "name": "bert-opt-v1",
      "version": "1.0.0",
      "backend": "onnx",
      "task": "fill-mask",
      "size_mb": 418.92,
      "created_at": "2026-01-30T10:30:00Z",
      "description": "BERT optimized with ONNX"
    }
  ],
  "total": 1
}
```

---

#### Get Model Info

Get detailed information about a specific model.

```http
GET /api/v1/registry/models/{model_name}
```

**Response:**

```json
{
  "name": "bert-opt-v1",
  "version": "1.0.0",
  "backend": "onnx",
  "task": "fill-mask",
  "size_mb": 418.92,
  "path": "./optimized_models/bert-base-uncased",
  "created_at": "2026-01-30T10:30:00Z",
  "updated_at": "2026-01-30T10:30:00Z",
  "description": "BERT optimized with ONNX Runtime",
  "tags": ["bert", "fill-mask", "onnx"],
  "metadata": {
    "quantization": true,
    "batch_size": 1,
    "sequence_length": 128
  }
}
```

---

#### Run Inference

Run inference on a registered model.

```http
POST /api/v1/registry/models/{model_name}/predict
Content-Type: application/json

{
  "input": "Paris is the capital of [MASK].",
  "top_k": 5
}
```

**Response:**

```json
{
  "model": "bert-opt-v1",
  "task": "fill-mask",
  "predictions": [
    {
      "token": "france",
      "score": 0.9821,
      "token_id": 2605
    },
    {
      "token": "europe",
      "score": 0.0087,
      "token_id": 2885
    }
  ],
  "inference_time_ms": 12.45
}
```

---

#### Create A/B Test

Create a new A/B test.

```http
POST /api/v1/ab-tests
Content-Type: application/json

{
  "name": "onnx-vs-openvino",
  "model_a": "bert-opt-v1",
  "model_b": "bert-opt-v2",
  "description": "Compare ONNX vs OpenVINO"
}
```

**Response:**

```json
{
  "test_id": "test_123",
  "name": "onnx-vs-openvino",
  "status": "created",
  "created_at": "2026-01-30T10:30:00Z"
}
```

---

#### Run A/B Test

Execute an A/B test.

```http
POST /api/v1/ab-tests/{test_id}/run
Content-Type: application/json

{
  "input": "The capital of France is [MASK].",
  "iterations": 100
}
```

**Response:**

```json
{
  "test_id": "test_123",
  "status": "completed",
  "results": {
    "model_a": {
      "name": "bert-opt-v1",
      "throughput": 46.44,
      "latency_ms": 21.53,
      "size_mb": 508.29
    },
    "model_b": {
      "name": "bert-opt-v2",
      "throughput": 43.36,
      "latency_ms": 23.07,
      "size_mb": 418.92
    },
    "winner": "model_a",
    "speedup": 1.07
  }
}
```

---

#### List A/B Tests

Get all A/B tests.

```http
GET /api/v1/ab-tests
```

**Response:**

```json
{
  "tests": [
    {
      "test_id": "test_123",
      "name": "onnx-vs-openvino",
      "model_a": "bert-opt-v1",
      "model_b": "bert-opt-v2",
      "status": "completed",
      "created_at": "2026-01-30T10:30:00Z"
    }
  ],
  "total": 1
}
```

---

## 🎨 Web Interface

### Features

The web interface provides a beautiful, gradient-themed UI for managing models:

#### 1. **Models Tab** 📊
- View all registered models in a grid layout
- See model details: name, version, backend, size, task
- Quick actions: test model, view details, delete
- Real-time model count

#### 2. **Inference Tab** 🎯
- Select any registered model from dropdown
- Enter custom input text
- Run inference with one click
- View predictions with scores
- See inference time

#### 3. **A/B Testing Tab** 🧪
- Create new A/B tests
- Select two models to compare
- Configure test parameters (iterations)
- Run comparisons
- View results in a formatted table:
  - Throughput (req/s)
  - Latency (ms)
  - Model size (MB)
  - Memory usage
  - Winner indication with visual badges

### Screenshots

**Models Tab:**
```
┌─────────────────────────────────────────────────┐
│  🚀 Optimum CLI Pro                              │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│  [Models] [Inference] [A/B Testing]              │
│                                                   │
│  📦 Registered Models (2)                        │
│                                                   │
│  ┌─────────────────┐  ┌─────────────────┐       │
│  │ bert-opt-v1     │  │ bert-opt-v2     │       │
│  │ v1.0.0          │  │ v1.0.0          │       │
│  │ Backend: onnx   │  │ Backend: openvino│      │
│  │ Size: 418.92 MB │  │ Size: 508.29 MB │       │
│  │ [Test] [Info]   │  │ [Test] [Info]   │       │
│  └─────────────────┘  └─────────────────┘       │
└─────────────────────────────────────────────────┘
```

### Accessing the UI

1. Start the server:
   ```bash
   optimum-pro serve start --port 8000
   ```

2. Open your browser:
   ```
   http://localhost:8000
   ```

3. The UI will load automatically with all features available

---

## 📦 Model Registry

### Database Schema

The registry uses SQLite with three main tables:

#### `models` Table

```sql
CREATE TABLE models (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    version TEXT NOT NULL,
    backend TEXT NOT NULL,
    task TEXT,
    path TEXT NOT NULL,
    size_mb REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT,
    tags TEXT,
    metadata TEXT
);
```

#### `ab_tests` Table

```sql
CREATE TABLE ab_tests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    model_a_id INTEGER NOT NULL,
    model_b_id INTEGER NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (model_a_id) REFERENCES models (id),
    FOREIGN KEY (model_b_id) REFERENCES models (id)
);
```

#### `ab_results` Table

```sql
CREATE TABLE ab_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_id INTEGER NOT NULL,
    model_a_throughput REAL,
    model_a_latency REAL,
    model_b_throughput REAL,
    model_b_latency REAL,
    winner TEXT,
    speedup REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (test_id) REFERENCES ab_tests (id)
);
```

### Registry Location

Default location: `./data/registry.db`

You can change this via:
- Environment variable: `REGISTRY_DB_PATH`
- Config file: `registry.db_path`

### Backup and Restore

```bash
# Backup registry
cp ./data/registry.db ./backups/registry_backup_$(date +%Y%m%d).db

# Restore registry
cp ./backups/registry_backup_20260130.db ./data/registry.db
```

---

## 🧪 A/B Testing

### What is A/B Testing?

A/B testing compares two models side-by-side to determine which performs better. The CLI runs multiple iterations and measures:

- **Throughput**: Requests per second
- **Latency**: Average response time
- **Memory**: RAM usage during inference
- **Size**: Model file size

### Best Practices

1. **Use Same Input**: Always use identical input for fair comparison
2. **Multiple Iterations**: Run at least 100 iterations for statistical significance
3. **Warm-up**: The CLI automatically warms up models before testing
4. **Same Hardware**: Run tests on the same machine for consistency

### Interpreting Results

```
Model A (ONNX):     46.44 req/s, 508.29 MB
Model B (OpenVINO): 43.36 req/s, 418.92 MB

Winner: Model A (1.07x faster)
Trade-off: Model A is 89.37 MB larger
```

**Decision Guide:**
- **If speed is critical** → Choose Model A (ONNX)
- **If size is critical** → Choose Model B (OpenVINO)
- **If balanced** → Consider 1.07x speedup vs 89 MB size increase

---

## 🏗️ Architecture

### Project Structure

```
optimum-cli-pro/
├── src/
│   └── optimum_cli/
│       ├── __init__.py
│       ├── __main__.py              # Entry point
│       ├── cli/
│       │   ├── __init__.py
│       │   ├── main.py              # Main CLI app (Typer)
│       │   ├── optimize.py          # Optimize commands
│       │   ├── registry.py          # Registry commands
│       │   └── serve.py             # Serve commands
│       ├── core/
│       │   ├── __init__.py
│       │   ├── config.py            # Configuration management
│       │   ├── model_loader.py      # Model loading & task detection
│       │   ├── optimizer.py         # Optimization logic
│       │   └── registry.py          # Registry database operations
│       ├── backends/
│       │   ├── __init__.py
│       │   ├── base.py              # Abstract base backend
│       │   ├── onnx_backend.py      # ONNX Runtime backend
│       │   ├── openvino_backend.py  # OpenVINO backend
│       │   └── better_transformer.py # BetterTransformer backend
│       └── api/
│           ├── __init__.py
│           ├── main.py              # FastAPI app
│           ├── routes/
│           │   ├── __init__.py
│           │   ├── health.py        # Health endpoints
│           │   ├── registry.py      # Registry endpoints
│           │   └── ab_testing.py    # A/B testing endpoints
│           └── static/
│               ├── index.html       # Main web UI
│               ├── style.css        # Gradient theme CSS
│               └── app.js           # Frontend JavaScript
├── data/
│   └── registry.db                  # SQLite database
├── optimized_models/                # Optimized model storage
├── deployment/
│   ├── docker/
│   │   ├── Dockerfile
│   │   └── docker-compose.yml
│   └── aws/
│       ├── cloudformation.yaml
│       └── deploy.sh
├── tests/
│   ├── unit/
│   └── integration/
├── docs/
├── pyproject.toml                   # Project configuration
├── requirements.txt                 # Python dependencies
├── .env.example                     # Environment template
└── README.md                        # This file
```

### Technology Stack

- **CLI Framework**: Typer + Rich (beautiful terminal UI)
- **API Framework**: FastAPI (async, high-performance)
- **Database**: SQLite with aiosqlite (async operations)
- **Model Loading**: HuggingFace Transformers + Optimum
- **Optimization Backends**:
  - ONNX Runtime (`optimum[onnxruntime]`)
  - OpenVINO (`optimum-intel`)
  - BetterTransformer (native PyTorch)
- **Frontend**: Vanilla JavaScript + CSS (no frameworks)
- **Configuration**: Pydantic v2 settings management
- **Logging**: Python logging with rich formatting

---

## 💡 Examples

### Example 1: Optimize Multiple Models

```bash
# Optimize different model types
optimum-pro optimize model bert-base-uncased --backend onnx
optimum-pro optimize model gpt2 --backend onnx
optimum-pro optimize model google/vit-base-patch16-224 --backend openvino

# Register all of them
optimum-pro registry push --name bert-fill-mask --path ./optimized_models/bert-base-uncased --backend onnx
optimum-pro registry push --name gpt2-text-gen --path ./optimized_models/gpt2 --backend onnx
optimum-pro registry push --name vit-image-class --path ./optimized_models/vit-base-patch16-224 --backend openvino
```

### Example 2: Complete A/B Testing Workflow

```bash
# 1. Optimize same model with different backends
optimum-pro optimize model bert-base-uncased --backend onnx
optimum-pro registry push --name bert-onnx --path ./optimized_models/bert-base-uncased --backend onnx

optimum-pro optimize model bert-base-uncased --backend openvino
optimum-pro registry push --name bert-openvino --path ./optimized_models/bert-base-uncased --backend openvino

# 2. Create A/B test
optimum-pro registry ab-test \
  --name backend-comparison \
  --model-a bert-onnx \
  --model-b bert-openvino \
  --description "ONNX vs OpenVINO on Intel CPU"

# 3. Run comparison
optimum-pro registry ab-compare backend-comparison \
  --input "Machine learning is revolutionizing [MASK]." \
  --iterations 200

# 4. View results
optimum-pro registry ab-list
```

### Example 3: Production Deployment

```bash
# 1. Optimize for production
optimum-pro optimize model bert-large-uncased-whole-word-masking-finetuned-squad \
  --backend onnx \
  --quantization \
  --batch-size 8 \
  --sequence-length 512

# 2. Register with production metadata
optimum-pro registry push \
  --name "bert-qa-prod" \
  --path "./optimized_models/bert-large-uncased-whole-word-masking-finetuned-squad" \
  --backend onnx \
  --version "1.0.0" \
  --description "Production BERT Q&A model - INT8 quantized" \
  --tags "production,qa,quantized"

# 3. Start production server
optimum-pro serve start --host 0.0.0.0 --port 8000 --workers 4

# 4. Test via API
curl -X POST http://localhost:8000/api/v1/registry/models/bert-qa-prod/predict \
  -H "Content-Type: application/json" \
  -d '{
    "input": "What is machine learning?",
    "context": "Machine learning is a subset of artificial intelligence..."
  }'
```

### Example 4: MLflow Integration

```bash
# Start MLflow server
mlflow server --host 0.0.0.0 --port 5000

# Optimize with MLflow tracking
export MLFLOW_TRACKING_URI=http://localhost:5000
optimum-pro optimize model bert-base-uncased \
  --backend onnx \
  --track-mlflow

# View in MLflow UI
open http://localhost:5000
```

---

## 👨‍💻 Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/yourusername/optimum-cli-pro.git
cd optimum-cli-pro

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows

# Install in development mode with all dependencies
pip install -e ".[dev,all]"

# Install pre-commit hooks
pre-commit install
```

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=optimum_cli --cov-report=html --cov-report=term

# Run specific test file
pytest tests/unit/test_optimizer.py

# Run with verbose output
pytest -v -s
```

### Code Quality

```bash
# Format code
black src/ tests/
isort src/ tests/

# Lint code
flake8 src/ tests/
pylint src/

# Type checking
mypy src/
```

### Building Package

```bash
# Build distribution
python -m build

# Install built package
pip install dist/optimum_cli_pro-1.0.0-py3-none-any.whl
```

---

## 🐳 Deployment

### Docker Deployment

#### Build and Run

```bash
# Build Docker image
docker build -t optimum-cli-pro:latest .

# Run container
docker run -d \
  --name optimum-cli-pro \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/optimized_models:/app/optimized_models \
  optimum-cli-pro:latest

# View logs
docker logs -f optimum-cli-pro

# Stop container
docker stop optimum-cli-pro
```

#### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./optimized_models:/app/optimized_models
    environment:
      - API_HOST=0.0.0.0
      - API_PORT=8000
      - LOG_LEVEL=INFO
    restart: unless-stopped

  mlflow:
    image: ghcr.io/mlflow/mlflow:latest
    ports:
      - "5000:5000"
    command: mlflow server --host 0.0.0.0 --port 5000
    volumes:
      - ./mlflow:/mlflow
    restart: unless-stopped
```

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### AWS Deployment

#### Prerequisites

- AWS CLI configured
- AWS account with EC2 access
- Key pair created in AWS

#### Deploy with CloudFormation

```bash
cd deployment/aws

# Deploy stack
aws cloudformation create-stack \
  --stack-name optimum-cli-pro \
  --template-body file://cloudformation.yaml \
  --parameters \
    ParameterKey=KeyName,ParameterValue=your-key-pair \
    ParameterKey=InstanceType,ParameterValue=t2.micro

# Wait for completion
aws cloudformation wait stack-create-complete \
  --stack-name optimum-cli-pro

# Get public IP
aws cloudformation describe-stacks \
  --stack-name optimum-cli-pro \
  --query 'Stacks[0].Outputs[?OutputKey==`PublicIP`].OutputValue' \
  --output text
```

#### Manual EC2 Setup

```bash
# SSH into EC2 instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# Install dependencies
sudo apt update
sudo apt install -y python3-pip git

# Clone and install
git clone https://github.com/yourusername/optimum-cli-pro.git
cd optimum-cli-pro
pip3 install -e .

# Start server
optimum-pro serve start --host 0.0.0.0 --port 8000
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. "Command not found: optimum-pro"

**Solution:**
```bash
# Reinstall package
pip install -e .

# Or use full path
python -m optimum_cli optimize model bert-base-uncased --backend onnx
```

#### 2. "Model not found" error

**Solution:**
```bash
# Check HuggingFace Hub connection
pip install -U transformers

# Manually download model
from transformers import AutoModel
model = AutoModel.from_pretrained("bert-base-uncased")
```

#### 3. OpenVINO optimization fails

**Solution:**
```bash
# Install OpenVINO correctly
pip install optimum[openvino]
pip install openvino

# Verify installation
python -c "from optimum.intel import OVModelForMaskedLM; print('OK')"
```

#### 4. Server won't start on port 8000

**Solution:**
```bash
# Check if port is in use
netstat -ano | findstr :8000  # Windows
lsof -i :8000                 # Linux/Mac

# Use different port
optimum-pro serve start --port 8080
```

#### 5. "Too many indices for tensor" error (OpenVINO)

**Known Issue:** OpenVINO models may have tensor dimension issues with certain tasks.

**Solution:** Use ONNX backend instead:
```bash
optimum-pro optimize model bert-base-uncased --backend onnx
```

#### 6. Database locked error

**Solution:**
```bash
# Close all connections and restart server
optimum-pro serve stop
rm -f ./data/registry.db-journal
optimum-pro serve start
```

### Debug Mode

Enable debug logging:

```bash
# Set environment variable
export LOG_LEVEL=DEBUG

# Or use CLI flag (if implemented)
optimum-pro --debug optimize model bert-base-uncased --backend onnx
```

### Getting Help

- **GitHub Issues**: https://github.com/yourusername/optimum-cli-pro/issues
- **Documentation**: https://github.com/yourusername/optimum-cli-pro/docs
- **HuggingFace Forum**: https://discuss.huggingface.co/

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### Reporting Bugs

1. Check existing issues first
2. Create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - System info (OS, Python version)

### Suggesting Features

1. Open an issue with `[Feature Request]` tag
2. Describe the feature and use case
3. Explain why it would be useful

### Pull Requests

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass: `pytest`
6. Format code: `black src/ tests/`
7. Commit: `git commit -m 'Add amazing feature'`
8. Push: `git push origin feature/amazing-feature`
9. Open a Pull Request

### Code Style

- Follow PEP 8
- Use Black for formatting
- Add type hints
- Write docstrings
- Add tests

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **HuggingFace**: For the amazing Transformers and Optimum libraries
- **FastAPI**: For the high-performance web framework
- **Typer**: For the beautiful CLI framework
- **Rich**: For terminal formatting
- **Intel**: For OpenVINO toolkit
- **ONNX Runtime**: For cross-platform inference

---

## 📈 Roadmap

### Version 1.1 (Q2 2026)
- [ ] TensorRT backend support
- [ ] GPU optimization
- [ ] Batch inference API
- [ ] Model versioning with Git
- [ ] Prometheus metrics export

### Version 1.2 (Q3 2026)
- [ ] Kubernetes deployment
- [ ] Multi-model serving
- [ ] Model caching
- [ ] Authentication & authorization
- [ ] Rate limiting

### Version 2.0 (Q4 2026)
- [ ] Distributed inference
- [ ] Model ensembles
- [ ] AutoML for backend selection
- [ ] Advanced monitoring dashboard
- [ ] CI/CD integration

---

## 🌟 Star History

If you find this project useful, please consider giving it a star on GitHub! ⭐

---

## 📞 Contact

- **Author**: Your Name
- **Email**: your.email@example.com
- **GitHub**: @yourusername
- **Twitter**: @yourhandle

---

**Made with ❤️ for the ML community** | **Powered by HuggingFace Optimum**
