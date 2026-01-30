# 🚀 Quick Deployment Guide

Choose your deployment method:

## Option 1: AWS CloudFormation (Recommended)

### Windows PowerShell
```powershell
# Set your AWS key pair name
$env:KEY_NAME = "your-key-pair-name"
$env:AWS_REGION = "us-east-1"

# Run deployment
.\deployment\scripts\deploy.ps1
```

### Linux/Mac
```bash
# Set your AWS key pair name
export KEY_NAME="your-key-pair-name"
export AWS_REGION="us-east-1"

# Run deployment
chmod +x deployment/scripts/deploy.sh
./deployment/scripts/deploy.sh
```

### What it does:
- ✅ Creates EC2 t2.micro instance (Free Tier)
- ✅ Configures security groups
- ✅ Installs Docker & Docker Compose
- ✅ Clones and runs the application
- ✅ Returns public IP and URLs

**Time:** 5-10 minutes

---

## Option 2: Manual EC2 Setup

See detailed guide: [deployment/aws/README.md](deployment/aws/README.md)

**Steps:**
1. Launch EC2 t2.micro instance
2. SSH into instance
3. Install Python 3.10
4. Clone repository
5. Install dependencies
6. Run application

**Time:** 20-30 minutes

---

## Option 3: Docker Compose (Local or Remote)

```bash
# Build and run with Docker
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

---

## After Deployment

### Access Your Application

Open in browser:
```
http://YOUR_PUBLIC_IP:8000
```

### Check Health
```bash
curl http://YOUR_PUBLIC_IP:8000/health
```

### View Logs (EC2)
```bash
ssh -i your-key.pem ubuntu@YOUR_PUBLIC_IP
sudo journalctl -u optimum-cli-pro -f
```

---

## Cost Estimate

### AWS Free Tier (First 12 months)
- **Cost:** $0/month
- **Includes:** 750 hours of t2.micro (24/7 for 1 instance)

### After Free Tier
- **t2.micro:** ~$8.50/month (us-east-1)
- **EBS Storage:** $0.10/GB/month
- **Data Transfer:** $0.09/GB

---

## Important Files

- **requirements.txt** - Updated with exact versions
- **.gitignore** - Excludes __pycache__, .env, optimized_models
- **deployment/aws/cloudformation.yaml** - AWS infrastructure template
- **deployment/scripts/deploy.sh** - Linux/Mac deployment script
- **deployment/scripts/deploy.ps1** - Windows PowerShell deployment script
- **deployment/aws/README.md** - Detailed AWS deployment guide

---

## Quick Commands

### Optimize a model on AWS
```bash
ssh -i your-key.pem ubuntu@YOUR_PUBLIC_IP
cd optimum-cli-pro
source venv/bin/activate
optimum-pro optimize model bert-base-uncased --backend onnx
```

### Register and serve
```bash
optimum-pro registry push --name bert-opt --path ./optimized_models/bert-base-uncased --backend onnx
```

### Check registered models via API
```bash
curl http://YOUR_PUBLIC_IP:8000/api/v1/registry/models
```

---

## Troubleshooting

**Can't connect to server?**
1. Check security group allows port 8000
2. Wait 2-3 minutes after deployment
3. Check instance status in AWS Console

**Service not running?**
```bash
sudo systemctl status optimum-cli-pro
sudo journalctl -xe -u optimum-cli-pro
```

**Out of memory?**
```bash
# Add swap space
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

---

## Next Steps

- ✅ Configure HTTPS with Let's Encrypt
- ✅ Set up automated backups
- ✅ Add monitoring with CloudWatch
- ✅ Scale with Auto Scaling Groups

For detailed instructions, see [deployment/aws/README.md](deployment/aws/README.md)
