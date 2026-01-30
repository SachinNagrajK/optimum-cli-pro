#!/bin/bash

# AWS Deployment Script for Optimum CLI Pro
# Deploys to EC2 t2.micro (Free Tier)

set -e

echo "🚀 Deploying Optimum CLI Pro to AWS"
echo "===================================="
echo ""

# Configuration
STACK_NAME="${STACK_NAME:-optimum-cli-pro}"
TEMPLATE_FILE="deployment/aws/cloudformation.yaml"
KEY_NAME="${KEY_NAME:-my-key-pair}"
REGION="${AWS_REGION:-us-east-1}"

echo "Configuration:"
echo "  Stack Name: $STACK_NAME"
echo "  Key Pair: $KEY_NAME"
echo "  Region: $REGION"
echo ""

# Check AWS CLI
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not found. Please install it first:"
    echo "   pip install awscli"
    echo "   aws configure"
    exit 1
fi

# Verify AWS credentials
echo "🔐 Checking AWS credentials..."
if ! aws sts get-caller-identity --region $REGION &> /dev/null; then
    echo "❌ AWS credentials not configured. Run: aws configure"
    exit 1
fi
echo "✅ AWS credentials valid"
echo ""

# Check if key pair exists
echo "🔑 Verifying key pair..."
if ! aws ec2 describe-key-pairs --key-names $KEY_NAME --region $REGION &> /dev/null; then
    echo "❌ Key pair '$KEY_NAME' not found in region $REGION"
    echo "   Create one in AWS Console: EC2 → Key Pairs → Create Key Pair"
    exit 1
fi
echo "✅ Key pair found"
echo ""

# Check if stack exists
echo "📋 Checking if stack exists..."
if aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION &> /dev/null 2>&1; then
    echo "♻️  Stack exists. Updating..."
    OPERATION="update-stack"
    WAIT_OPERATION="stack-update-complete"
else
    echo "🆕 Creating new stack..."
    OPERATION="create-stack"
    WAIT_OPERATION="stack-create-complete"
fi
echo ""

# Deploy stack
echo "🔨 Deploying CloudFormation stack..."
echo "   This will take 5-10 minutes..."
echo ""

if aws cloudformation $OPERATION \
    --stack-name $STACK_NAME \
    --template-body file://$TEMPLATE_FILE \
    --parameters ParameterKey=KeyName,ParameterValue=$KEY_NAME \
    --region $REGION \
    --capabilities CAPABILITY_IAM 2>&1; then
    
    # Wait for completion
    echo "⏳ Waiting for deployment to complete..."
    if aws cloudformation wait $WAIT_OPERATION \
        --stack-name $STACK_NAME \
        --region $REGION; then
        
        echo ""
        echo "✅ Deployment complete!"
        echo ""
        
        # Get outputs
        echo "📊 Stack Outputs:"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        
        PUBLIC_IP=$(aws cloudformation describe-stacks \
            --stack-name $STACK_NAME \
            --region $REGION \
            --query 'Stacks[0].Outputs[?OutputKey==`PublicIP`].OutputValue' \
            --output text)
        
        PUBLIC_DNS=$(aws cloudformation describe-stacks \
            --stack-name $STACK_NAME \
            --region $REGION \
            --query 'Stacks[0].Outputs[?OutputKey==`PublicDNS`].OutputValue' \
            --output text)
        
        INSTANCE_ID=$(aws cloudformation describe-stacks \
            --stack-name $STACK_NAME \
            --region $REGION \
            --query 'Stacks[0].Outputs[?OutputKey==`InstanceId`].OutputValue' \
            --output text)
        
        echo "Instance ID:  $INSTANCE_ID"
        echo "Public IP:    $PUBLIC_IP"
        echo "Public DNS:   $PUBLIC_DNS"
        echo ""
        echo "🌐 Access URLs:"
        echo "   Web UI:  http://$PUBLIC_IP:8000"
        echo "   API:     http://$PUBLIC_IP:8000/docs"
        echo "   Health:  http://$PUBLIC_IP:8000/health"
        echo ""
        echo "🔌 SSH Access:"
        echo "   ssh -i $KEY_NAME.pem ubuntu@$PUBLIC_IP"
        echo ""
        echo "📝 Note: Wait 2-3 minutes for the application to start"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    else
        echo "❌ Deployment failed during wait"
        exit 1
    fi
else
    if [ "$OPERATION" == "update-stack" ]; then
        echo "⚠️  No updates to perform (stack unchanged)"
    else
        echo "❌ Deployment failed"
        exit 1
    fi
fi
echo "📊 Stack Outputs:"
aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --region $REGION \
    --query 'Stacks[0].Outputs' \
    --output table

echo ""
echo "🎉 Done! Your Optimum CLI Pro is now running on AWS."
echo ""
echo "💡 Tips:"
echo "  - API Docs: http://<public-ip>:8000/docs"
echo "  - Health Check: http://<public-ip>:8000/api/v1/health"
echo "  - SSH: ssh -i <key-file>.pem ubuntu@<public-ip>"
echo ""
echo "💰 Cost Estimate: $0-5/month (within free tier)"
