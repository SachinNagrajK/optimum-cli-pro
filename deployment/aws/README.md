# AWS Deployment Guide for Optimum CLI Pro

Complete guide to deploy Optimum CLI Pro on AWS EC2.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Deploy with CloudFormation](#quick-deploy-with-cloudformation)
3. [Manual EC2 Setup](#manual-ec2-setup)
4. [Configuration](#configuration)
5. [Monitoring](#monitoring)
6. [Troubleshooting](#troubleshooting)
7. [Cost Optimization](#cost-optimization)

---

## Prerequisites

### Required Tools

1. **AWS Account** with EC2 access
2. **AWS CLI** installed and configured:
   ```bash
   # Install AWS CLI
   pip install awscli
   
   # Configure credentials
   aws configure
   ```
   
3. **SSH Key Pair** created in AWS Console:
   - Go to EC2 → Key Pairs → Create Key Pair
   - Save the `.pem` file securely
   - On Windows, use PuTTY or PowerShell

4. **Git** installed on your local machine

### AWS Resources You'll Need

- **EC2 Instance**: t2.micro (Free Tier eligible)
- **Security Group**: With ports 22, 80, 8000 open
- **Elastic IP** (optional): For permanent public IP

---

## Quick Deploy with CloudFormation

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/optimum-cli-pro.git
cd optimum-cli-pro
```

### Step 2: Set Environment Variables

```bash
# Windows PowerShell
$env:KEY_NAME = "your-key-pair-name"
$env:AWS_REGION = "us-east-1"

# Linux/Mac
export KEY_NAME="your-key-pair-name"
export AWS_REGION="us-east-1"
```

### Step 3: Deploy with Script

```bash
# Make script executable (Linux/Mac)
chmod +x deployment/scripts/deploy.sh

# Run deployment
./deployment/scripts/deploy.sh
```

**Or deploy manually with AWS CLI:**

```bash
aws cloudformation create-stack \
  --stack-name optimum-cli-pro \
  --template-body file://deployment/aws/cloudformation.yaml \
  --parameters ParameterKey=KeyName,ParameterValue=your-key-pair \
  --region us-east-1
```

### Step 4: Wait for Completion

```bash
aws cloudformation wait stack-create-complete \
  --stack-name optimum-cli-pro \
  --region us-east-1
```

### Step 5: Get Your Server URL

```bash
# Get public IP
aws cloudformation describe-stacks \
  --stack-name optimum-cli-pro \
  --query 'Stacks[0].Outputs[?OutputKey==`PublicIP`].OutputValue' \
  --output text

# Output example: 54.123.45.67
```

### Step 6: Access the Application

Open in your browser:
```
http://YOUR_PUBLIC_IP:8000
```

---

## Manual EC2 Setup

If you prefer manual setup instead of CloudFormation:

### Step 1: Launch EC2 Instance

1. Go to AWS Console → EC2 → Launch Instance
2. **Choose AMI**: Ubuntu Server 22.04 LTS
3. **Instance Type**: t2.micro (Free Tier)
4. **Key Pair**: Select your SSH key
5. **Security Group**: Create/select with these rules:
   - SSH (22) from your IP
   - HTTP (80) from anywhere
   - Custom TCP (8000) from anywhere
6. **Storage**: 8 GB (Free Tier)
7. Launch instance

### Step 2: Connect to Instance

```bash
# Windows PowerShell
ssh -i "your-key.pem" ubuntu@YOUR_PUBLIC_IP

# Or use PuTTY on Windows
```

### Step 3: Install Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.10
sudo apt install -y python3.10 python3.10-venv python3-pip git

# Install required system packages
sudo apt install -y build-essential libssl-dev libffi-dev python3-dev
```

### Step 4: Clone and Setup Application

```bash
# Clone repository
cd /home/ubuntu
git clone https://github.com/yourusername/optimum-cli-pro.git
cd optimum-cli-pro

# Create virtual environment
python3.10 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 5: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit configuration
nano .env
```

Set these values:
```bash
API_HOST=0.0.0.0
API_PORT=8000
REGISTRY_DB_PATH=/home/ubuntu/optimum-cli-pro/data/registry.db
MODELS_DIR=/home/ubuntu/optimum-cli-pro/optimized_models
```

### Step 6: Create Systemd Service

Create a service file to run the app automatically:

```bash
sudo nano /etc/systemd/system/optimum-cli-pro.service
```

Add this content:

```ini
[Unit]
Description=Optimum CLI Pro API Server
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/optimum-cli-pro
Environment="PATH=/home/ubuntu/optimum-cli-pro/venv/bin"
ExecStart=/home/ubuntu/optimum-cli-pro/venv/bin/optimum-pro serve start --host 0.0.0.0 --port 8000
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable optimum-cli-pro
sudo systemctl start optimum-cli-pro

# Check status
sudo systemctl status optimum-cli-pro
```

### Step 7: Setup Nginx (Optional - for Port 80)

```bash
# Install Nginx
sudo apt install -y nginx

# Create configuration
sudo nano /etc/nginx/sites-available/optimum-cli-pro
```

Add this:

```nginx
server {
    listen 80;
    server_name YOUR_PUBLIC_IP;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/optimum-cli-pro /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

Now access via: `http://YOUR_PUBLIC_IP` (port 80)

---

## Configuration

### Environment Variables

Create `/home/ubuntu/optimum-cli-pro/.env`:

```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=2

# Database
REGISTRY_DB_PATH=/home/ubuntu/optimum-cli-pro/data/registry.db

# Storage
MODELS_DIR=/home/ubuntu/optimum-cli-pro/optimized_models

# Logging
LOG_LEVEL=INFO
LOG_FILE=/home/ubuntu/optimum-cli-pro/logs/api.log

# Security (recommended for production)
API_KEY=your-secret-api-key-here
ALLOWED_ORIGINS=*

# AWS Region (if using S3 for model storage)
AWS_REGION=us-east-1
```

### Firewall Configuration

```bash
# Allow only necessary ports
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 8000/tcp # API
sudo ufw enable
```

---

## Monitoring

### Check Application Logs

```bash
# View service logs
sudo journalctl -u optimum-cli-pro -f

# View application logs
tail -f /home/ubuntu/optimum-cli-pro/logs/api.log
```

### Health Check

```bash
# From server
curl http://localhost:8000/health

# From your computer
curl http://YOUR_PUBLIC_IP:8000/health
```

### Resource Monitoring

```bash
# Install htop
sudo apt install -y htop

# Monitor resources
htop

# Check disk space
df -h

# Check memory
free -m
```

### CloudWatch Integration (Optional)

Install CloudWatch agent:

```bash
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
sudo dpkg -i -E ./amazon-cloudwatch-agent.deb
```

---

## Troubleshooting

### Issue: Service Won't Start

```bash
# Check status
sudo systemctl status optimum-cli-pro

# View detailed logs
sudo journalctl -xe -u optimum-cli-pro

# Check Python path
which python
/home/ubuntu/optimum-cli-pro/venv/bin/python --version
```

### Issue: Can't Access from Browser

1. **Check Security Group**:
   - AWS Console → EC2 → Security Groups
   - Ensure port 8000 is open to 0.0.0.0/0

2. **Check if service is running**:
   ```bash
   sudo systemctl status optimum-cli-pro
   curl http://localhost:8000/health
   ```

3. **Check firewall**:
   ```bash
   sudo ufw status
   ```

### Issue: Out of Memory

```bash
# Check memory usage
free -m

# Add swap space (for t2.micro)
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Make permanent
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### Issue: Disk Space Full

```bash
# Check disk usage
df -h

# Clean up
sudo apt autoremove -y
sudo apt clean

# Remove old logs
sudo journalctl --vacuum-time=7d
```

---

## Cost Optimization

### Free Tier Usage

AWS Free Tier includes:
- **750 hours/month** of t2.micro instance (enough for 24/7)
- **30 GB** of EBS storage
- **15 GB** of bandwidth out

### Tips to Stay in Free Tier

1. **Use t2.micro only**: Don't upgrade to larger instances
2. **Stop instance when not needed**:
   ```bash
   aws ec2 stop-instances --instance-ids i-1234567890abcdef0
   ```
3. **Monitor usage**: AWS Console → Billing Dashboard
4. **Set billing alerts**: Get notified if costs exceed $0

### After Free Tier

If you exceed free tier limits:
- t2.micro: ~$8.50/month (us-east-1)
- EBS storage: $0.10/GB/month
- Data transfer: $0.09/GB

**Cost-saving options**:
- Use **Spot Instances**: 70-90% cheaper
- Use **Lightsail**: Fixed $3.50/month for similar specs
- Stop instance during off-hours

---

## Updating the Application

### Pull Latest Changes

```bash
cd /home/ubuntu/optimum-cli-pro
git pull origin main

# Restart service
sudo systemctl restart optimum-cli-pro
```

### Update Dependencies

```bash
source venv/bin/activate
pip install -r requirements.txt --upgrade
sudo systemctl restart optimum-cli-pro
```

---

## Backup and Restore

### Backup Registry Database

```bash
# Create backup directory
mkdir -p /home/ubuntu/backups

# Backup database
cp /home/ubuntu/optimum-cli-pro/data/registry.db \
   /home/ubuntu/backups/registry_$(date +%Y%m%d_%H%M%S).db

# Backup to S3 (optional)
aws s3 cp /home/ubuntu/optimum-cli-pro/data/registry.db \
   s3://your-bucket/backups/registry_$(date +%Y%m%d).db
```

### Automated Backups

Create a cron job:

```bash
crontab -e
```

Add this line (backup daily at 2 AM):

```bash
0 2 * * * cp /home/ubuntu/optimum-cli-pro/data/registry.db /home/ubuntu/backups/registry_$(date +\%Y\%m\%d).db
```

---

## Security Best Practices

1. **Change default SSH port**:
   ```bash
   sudo nano /etc/ssh/sshd_config
   # Change Port 22 to Port 2222
   sudo systemctl restart sshd
   ```

2. **Disable root login**:
   ```bash
   sudo nano /etc/ssh/sshd_config
   # Set PermitRootLogin no
   ```

3. **Enable firewall**:
   ```bash
   sudo ufw enable
   ```

4. **Install fail2ban**:
   ```bash
   sudo apt install -y fail2ban
   ```

5. **Use HTTPS** (with Let's Encrypt):
   ```bash
   sudo apt install -y certbot python3-certbot-nginx
   sudo certbot --nginx
   ```

---

## Next Steps

- ✅ Monitor your application with CloudWatch
- ✅ Set up automated backups
- ✅ Configure HTTPS with SSL certificate
- ✅ Add authentication to your API
- ✅ Scale horizontally with multiple instances behind a load balancer

---

## Support

For issues or questions:
- GitHub Issues: https://github.com/yourusername/optimum-cli-pro/issues
- Documentation: [Main README](../../README.md)

---

**Happy Deploying! 🚀**
