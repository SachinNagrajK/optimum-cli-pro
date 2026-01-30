# 🎉 Optimum CLI Pro - Getting Started

Congratulations! Your production-grade model optimization toolkit is ready!

## 📁 Project Structure

Your project has been successfully created with the following structure:

```
optimum-cli-pro/
├── src/optimum_cli/          # Main source code
│   ├── api/                  # FastAPI server
│   ├── backends/             # Optimization backends
│   ├── cli/                  # CLI commands
│   ├── core/                 # Core logic
│   └── utils/                # Utilities
├── configs/                  # Configuration files
├── deployment/               # Deployment configs
├── tests/                    # Test suite
├── docs/                     # Documentation
├── Dockerfile               # Docker configuration
├── docker-compose.yml       # Docker Compose
└── requirements.txt         # Dependencies
```

## 🚀 Installation & Setup

### Step 1: Navigate to the project

```powershell
cd s:\Studies\Projects\hf\huggingface-demos-main\optimum\optimum-cli-pro
```

### Step 2: Create virtual environment

```powershell
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install dependencies

```powershell
# Install core dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .
```

### Step 4: Set up environment

```powershell
# Copy environment template
copy .env.example .env

# Edit .env if needed
```

## ✨ Quick Start

### 1. Check Installation

```powershell
# Check version
optimum-cli version

# View system information
optimum-cli info

# List available backends
optimum-cli list-backends
```

### 2. Optimize Your First Model

```powershell
# Simple optimization with auto-detection
optimum-cli optimize model bert-base-uncased

# Specify backend
optimum-cli optimize model bert-base-uncased --backend onnx

# With custom output directory
optimum-cli optimize model distilbert-base-uncased --backend openvino --output ./my_models

# Disable quantization
optimum-cli optimize model roberta-base --backend onnx --no-quantization
```

### 3. Get Model Information

```powershell
# Get details about any model
optimum-cli optimize info bert-base-uncased

# List optimized models
optimum-cli optimize list
```

### 4. Start the API Server

```powershell
# Start server
optimum-cli serve start

# Start on custom port
optimum-cli serve start --port 8080

# Development mode with auto-reload
optimum-cli serve start --reload
```

Then open your browser:
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/api/v1/health

## 🔧 CLI Commands Reference

### Optimize Commands

```powershell
optimum-cli optimize model <model-id> [OPTIONS]
optimum-cli optimize info <model-id>
optimum-cli optimize list
```

**Options:**
- `--backend, -b`: Backend to use (auto, onnx, openvino, bettertransformer)
- `--output, -o`: Output directory
- `--task, -t`: Task type
- `--batch-size`: Batch size
- `--sequence-length`: Sequence length
- `--quantization/--no-quantization`: Enable/disable quantization
- `--track-mlflow`: Track with MLflow
- `--track-wandb`: Track with Weights & Biases

### Benchmark Commands (Coming Soon)

```powershell
optimum-cli benchmark model <model-id> [OPTIONS]
optimum-cli benchmark compare <model-a> <model-b>
```

### Registry Commands (Coming Soon)

```powershell
optimum-cli registry list
optimum-cli registry push <name> <path>
optimum-cli registry pull <name>
optimum-cli registry delete <name>
```

### Server Commands

```powershell
optimum-cli serve start [OPTIONS]
```

**Options:**
- `--host, -h`: Host to bind (default: 0.0.0.0)
- `--port, -p`: Port to bind (default: 8000)
- `--workers, -w`: Number of workers (default: 1)
- `--reload`: Enable auto-reload

## 🌐 API Usage

### Using cURL

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Optimize a model
curl -X POST http://localhost:8000/api/v1/optimize \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": "bert-base-uncased",
    "backend": "onnx",
    "quantization": true
  }'

# Get model info
curl http://localhost:8000/api/v1/models/info/bert-base-uncased

# List backends
curl http://localhost:8000/api/v1/backends
```

### Using Python

```python
import requests

# Optimize a model
response = requests.post(
    "http://localhost:8000/api/v1/optimize",
    json={
        "model_id": "bert-base-uncased",
        "backend": "onnx",
        "quantization": True
    }
)
print(response.json())
```

## 🐳 Docker Deployment

### Build and Run

```powershell
# Build image
docker build -t optimum-cli-pro .

# Run container
docker run -p 8000:8000 optimum-cli-pro
```

### Using Docker Compose

```powershell
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## ☁️ AWS Deployment

### Prerequisites

1. AWS account
2. AWS CLI installed and configured
3. EC2 key pair created

### Deploy to AWS Free Tier

```powershell
# Set your key pair name
$env:KEY_NAME="my-key-pair"
$env:AWS_REGION="us-east-1"

# Navigate to deployment scripts
cd deployment\scripts

# Deploy (on Linux/Mac, make executable first: chmod +x deploy.sh)
bash deploy.sh
```

**Estimated Cost:** $0-5/month (within free tier limits)

## 📊 Supported Backends

| Backend | Best For | Hardware | Status |
|---------|----------|----------|--------|
| **ONNX Runtime** | Cross-platform | CPU/GPU | ✅ Ready |
| **OpenVINO** | Intel CPUs | Intel | ✅ Ready |
| **BetterTransformer** | Quick optimization | CPU/GPU | ✅ Ready |

## 🔍 Examples

### Example 1: Optimize BERT for CPU

```powershell
optimum-cli optimize model bert-base-uncased \
  --backend openvino \
  --quantization \
  --output ./optimized_bert
```

### Example 2: Optimize DistilBERT with ONNX

```powershell
optimum-cli optimize model distilbert-base-uncased \
  --backend onnx \
  --batch-size 1 \
  --sequence-length 128
```

### Example 3: Optimize Vision Transformer

```powershell
optimum-cli optimize model google/vit-base-patch16-224 \
  --backend onnx \
  --task image-classification
```

## 🛠️ Configuration

Edit `configs/default.yaml` to customize:

```yaml
optimization:
  default_backend: "auto"
  quantization:
    enabled: true
    mode: "dynamic"
    bits: 8

benchmarking:
  warmup_runs: 5
  test_runs: 50

logging:
  level: "INFO"
  file:
    enabled: true
    path: "./data/logs/app.log"
```

## 🧪 Testing

```powershell
# Run all tests
pytest

# Run with coverage
pytest --cov=optimum_cli --cov-report=html

# Run specific test
pytest tests/unit/test_backends.py
```

## 📚 Documentation

- [Quick Start](docs/quickstart.md)
- [CLI Guide](docs/cli-guide.md) (coming soon)
- [API Guide](docs/api-guide.md) (coming soon)
- [AWS Deployment](docs/aws-deployment.md) (coming soon)

## 🐛 Troubleshooting

### Issue: Backend not available

**Solution:** Install backend dependencies

```powershell
# For OpenVINO
pip install "optimum[openvino,nncf]"

# For all backends
pip install -e ".[all]"
```

### Issue: Out of memory

**Solution:** Reduce batch size or use a lighter backend

```powershell
optimum-cli optimize model bert-large --backend onnx --batch-size 1
```

### Issue: Model not found

**Solution:** Verify model ID on HuggingFace Hub
- Visit: https://huggingface.co/models
- Search for your model
- Use exact model ID

## 🎯 Next Steps

1. ✅ **Start optimizing** your models
2. 📊 **Explore different backends** to find the best performance
3. 🚀 **Deploy to AWS** for production use
4. 📈 **Track experiments** with MLflow/WandB (coming soon)
5. 🔄 **Benchmark** and compare backends (coming soon)

## 💡 Tips

- Use `--backend auto` to let the system choose the best backend
- Start with smaller models to test your setup
- Check `optimum-cli info` to see hardware capabilities
- Use `--quantization` for better performance with minimal accuracy loss
- Monitor logs in `./data/logs/app.log`

## 🤝 Need Help?

- Check the logs: `./data/logs/app.log`
- Run `optimum-cli info` to check system status
- Review configuration in `configs/default.yaml`

---

## 🎉 Congratulations!

You now have a production-grade model optimization toolkit!

**Start optimizing with:**
```powershell
optimum-cli optimize model bert-base-uncased --backend auto
```

Happy optimizing! 🚀
