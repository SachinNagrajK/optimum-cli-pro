# 🎯 AWS Deployment Quick Reference Card

## Prerequisites Checklist

- [ ] AWS Account created
- [ ] AWS CLI installed: `pip install awscli`
- [ ] AWS credentials configured: `aws configure`
- [ ] EC2 Key Pair created (save .pem file)
- [ ] Git repository ready (optional: push to GitHub)

---

## Deploy to AWS (Windows)

```powershell
# 1. Set your key pair name
$env:KEY_NAME = "my-aws-key"
$env:AWS_REGION = "us-east-1"

# 2. Run deployment
cd S:\Studies\Projects\hf\huggingface-demos-main\optimum\optimum-cli-pro
.\deployment\scripts\deploy.ps1

# 3. Wait 5-10 minutes
# Script will output: http://YOUR_IP:8000
```

---

## Deploy to AWS (Linux/Mac)

```bash
# 1. Set your key pair name
export KEY_NAME="my-aws-key"
export AWS_REGION="us-east-1"

# 2. Run deployment
cd /path/to/optimum-cli-pro
chmod +x deployment/scripts/deploy.sh
./deployment/scripts/deploy.sh

# 3. Wait 5-10 minutes
# Script will output: http://YOUR_IP:8000
```

---

## After Deployment

### Access Application
```
Web UI:  http://YOUR_PUBLIC_IP:8000
API:     http://YOUR_PUBLIC_IP:8000/docs
Health:  http://YOUR_PUBLIC_IP:8000/health
```

### SSH into Server
```bash
ssh -i your-key.pem ubuntu@YOUR_PUBLIC_IP
```

### Check Status
```bash
# On server
sudo systemctl status optimum-cli-pro
sudo journalctl -u optimum-cli-pro -f
```

---

## Common AWS Commands

### Check Stack Status
```bash
aws cloudformation describe-stacks \
  --stack-name optimum-cli-pro \
  --region us-east-1
```

### Get Public IP
```bash
aws cloudformation describe-stacks \
  --stack-name optimum-cli-pro \
  --query 'Stacks[0].Outputs[?OutputKey==`PublicIP`].OutputValue' \
  --output text
```

### Delete Stack (Cleanup)
```bash
aws cloudformation delete-stack \
  --stack-name optimum-cli-pro \
  --region us-east-1
```

### Stop Instance (Save Money)
```bash
# Get instance ID first
INSTANCE_ID=$(aws cloudformation describe-stacks \
  --stack-name optimum-cli-pro \
  --query 'Stacks[0].Outputs[?OutputKey==`InstanceId`].OutputValue' \
  --output text)

# Stop instance
aws ec2 stop-instances --instance-ids $INSTANCE_ID

# Start instance later
aws ec2 start-instances --instance-ids $INSTANCE_ID
```

---

## Git Commands (Before Pushing)

```bash
# Add files
git add .

# Check what will be committed (verify .gitignore works)
git status

# Should NOT see:
# - __pycache__/
# - .venv/
# - optimized_models/
# - data/registry.db
# - .env

# Commit
git commit -m "Add production-ready optimum-cli-pro with AWS deployment"

# Push to GitHub
git remote add origin https://github.com/yourusername/optimum-cli-pro.git
git push -u origin main
```

---

## Files Ready for Git

### ✅ Will be committed:
- `src/` - All source code
- `deployment/` - AWS templates and scripts
- `requirements.txt` - Updated dependencies
- `.gitignore` - Comprehensive exclusions
- `README.md` - Complete documentation
- `DEPLOYMENT.md` - Quick deployment guide
- `pyproject.toml` - Package configuration
- `Dockerfile` - Docker setup
- `docker-compose.yml` - Multi-container setup

### ❌ Excluded by .gitignore:
- `__pycache__/` - Python bytecode
- `.venv/` - Virtual environment
- `optimized_models/` - Large model files
- `data/registry.db` - Local database
- `.env` - Environment secrets
- `*.log` - Log files

---

## Cost Management

### Free Tier (12 months)
- ✅ 750 hours/month of t2.micro = $0
- ✅ 30 GB storage = $0
- ✅ 15 GB bandwidth = $0

### After Free Tier
- 💰 t2.micro 24/7 = ~$8.50/month
- 💰 8 GB storage = $0.80/month
- 💰 Total = ~$9.30/month

### Save Money
```bash
# Stop instance when not using
aws ec2 stop-instances --instance-ids YOUR_INSTANCE_ID

# Start when needed
aws ec2 start-instances --instance-ids YOUR_INSTANCE_ID
```

---

## Troubleshooting

### Can't connect to http://PUBLIC_IP:8000?

**1. Check security group:**
```bash
aws ec2 describe-security-groups \
  --filters "Name=group-name,Values=*optimum*" \
  --query 'SecurityGroups[0].IpPermissions'
```
Should show port 8000 open.

**2. Wait 2-3 minutes:** Application takes time to start

**3. Check service:**
```bash
ssh -i your-key.pem ubuntu@YOUR_PUBLIC_IP
sudo systemctl status optimum-cli-pro
```

### Out of memory on t2.micro?

```bash
# Add 2GB swap
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Service won't start?

```bash
# Check logs
sudo journalctl -xe -u optimum-cli-pro

# Restart
sudo systemctl restart optimum-cli-pro
```

---

## Update Application

### On AWS Instance:

```bash
# SSH into server
ssh -i your-key.pem ubuntu@YOUR_PUBLIC_IP

# Pull latest changes
cd /home/ubuntu/optimum-cli-pro
git pull origin main

# Update dependencies
source venv/bin/activate
pip install -r requirements.txt --upgrade

# Restart service
sudo systemctl restart optimum-cli-pro
```

---

## Security Best Practices

1. **Change default ports** (optional)
2. **Use HTTPS** with Let's Encrypt:
   ```bash
   sudo apt install -y certbot python3-certbot-nginx
   sudo certbot --nginx
   ```
3. **Restrict SSH access** to your IP only
4. **Enable firewall**:
   ```bash
   sudo ufw allow 22/tcp
   sudo ufw allow 80/tcp
   sudo ufw allow 8000/tcp
   sudo ufw enable
   ```
5. **Add API authentication** (see README.md)

---

## Support & Documentation

- 📖 **Main README**: [README.md](README.md)
- 🚀 **Quick Deploy**: [DEPLOYMENT.md](DEPLOYMENT.md)
- ☁️ **AWS Guide**: [deployment/aws/README.md](deployment/aws/README.md)
- 🐛 **Issues**: GitHub Issues page

---

**Happy Deploying! 🎉**
