# 🚀 Quick Start Guide

## Installation

### Option 1: Install from Source

```bash
# Clone the repository
git clone https://github.com/yourusername/optimum-cli-pro.git
cd optimum-cli-pro

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

### Option 2: Install with pip (when published)

```bash
pip install optimum-cli-pro
```

## First Steps

### 1. Check Installation

```bash
optimum-cli version
optimum-cli info
```

### 2. Optimize Your First Model

```bash
# Optimize with auto-selected backend
optimum-cli optimize model bert-base-uncased

# Optimize with specific backend
optimum-cli optimize model bert-base-uncased --backend onnx

# Optimize with quantization
optimum-cli optimize model distilbert-base-uncased --backend openvino --quantization
```

### 3. Start the API Server

```bash
# Start server on default port (8000)
optimum-cli serve start

# Start with custom port
optimum-cli serve start --port 8080

# Start with auto-reload for development
optimum-cli serve start --reload
```

### 4. Access API Documentation

Open your browser and navigate to:
- Interactive API docs: `http://localhost:8000/docs`
- Alternative docs: `http://localhost:8000/redoc`

## Common Commands

```bash
# Get model information
optimum-cli optimize info bert-base-uncased

# List available backends
optimum-cli list-backends

# List optimized models
optimum-cli optimize list

# Benchmark a model (coming soon)
optimum-cli benchmark model bert-base-uncased --backends all

# Model registry (coming soon)
optimum-cli registry list
optimum-cli registry push my-model ./optimized_models/bert_onnx
optimum-cli registry pull my-model
```

## Docker Deployment

```bash
# Build image
docker build -t optimum-cli-pro .

# Run container
docker run -p 8000:8000 optimum-cli-pro

# Or use Docker Compose
docker-compose up -d
```

## AWS Deployment

```bash
# Set your AWS key pair name
export KEY_NAME=my-key-pair
export AWS_REGION=us-east-1

# Deploy to AWS
cd deployment/scripts
chmod +x deploy.sh
./deploy.sh
```

## Configuration

Edit `.env` file or set environment variables:

```bash
# Application
APP_NAME=optimum-cli-pro
ENVIRONMENT=production
DEBUG=false

# Server
HOST=0.0.0.0
PORT=8000

# MLOps (optional)
MLFLOW_ENABLED=false
WANDB_ENABLED=false
```

## Next Steps

- [CLI Guide](cli-guide.md) - Detailed CLI documentation
- [API Guide](api-guide.md) - API reference
- [AWS Deployment](aws-deployment.md) - Detailed AWS setup

## Troubleshooting

### Missing Dependencies

```bash
# Install all optional dependencies
pip install -e ".[all]"

# Or install specific backends
pip install "optimum[openvino,nncf]"  # OpenVINO
```

### Backend Not Available

Check if required packages are installed:

```bash
optimum-cli info  # Shows which backends are available
```

### Out of Memory

Reduce batch size or try a different backend:

```bash
optimum-cli optimize model bert-large --backend onnx --batch-size 1
```

## Need Help?

- Check the [issues](https://github.com/yourusername/optimum-cli-pro/issues)
- Read the [documentation](https://github.com/yourusername/optimum-cli-pro/docs)
- Contact support

---

Happy optimizing! 🎉
