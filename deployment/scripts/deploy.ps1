# AWS Deployment Script for Optimum CLI Pro (PowerShell)
# Deploys to EC2 t2.micro (Free Tier)

$ErrorActionPreference = "Stop"

Write-Host "🚀 Deploying Optimum CLI Pro to AWS" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$STACK_NAME = if ($env:STACK_NAME) { $env:STACK_NAME } else { "optimum-cli-pro" }
$TEMPLATE_FILE = "deployment\aws\cloudformation.yaml"
$KEY_NAME = if ($env:KEY_NAME) { $env:KEY_NAME } else { "my-key-pair" }
$REGION = if ($env:AWS_REGION) { $env:AWS_REGION } else { "us-east-1" }

Write-Host "Configuration:" -ForegroundColor Yellow
Write-Host "  Stack Name: $STACK_NAME"
Write-Host "  Key Pair: $KEY_NAME"
Write-Host "  Region: $REGION"
Write-Host ""

# Check AWS CLI
try {
    $null = Get-Command aws -ErrorAction Stop
    Write-Host "✅ AWS CLI found" -ForegroundColor Green
} catch {
    Write-Host "❌ AWS CLI not found. Please install it first:" -ForegroundColor Red
    Write-Host "   Install-Module -Name AWSPowerShell" -ForegroundColor Yellow
    Write-Host "   Or download from: https://aws.amazon.com/cli/" -ForegroundColor Yellow
    exit 1
}

# Verify AWS credentials
Write-Host "🔐 Checking AWS credentials..." -ForegroundColor Yellow
try {
    aws sts get-caller-identity --region $REGION --output json | Out-Null
    Write-Host "✅ AWS credentials valid" -ForegroundColor Green
} catch {
    Write-Host "❌ AWS credentials not configured. Run: aws configure" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Check if key pair exists
Write-Host "🔑 Verifying key pair..." -ForegroundColor Yellow
try {
    aws ec2 describe-key-pairs --key-names $KEY_NAME --region $REGION --output json | Out-Null
    Write-Host "✅ Key pair found" -ForegroundColor Green
} catch {
    Write-Host "❌ Key pair '$KEY_NAME' not found in region $REGION" -ForegroundColor Red
    Write-Host "   Create one in AWS Console: EC2 → Key Pairs → Create Key Pair" -ForegroundColor Yellow
    exit 1
}
Write-Host ""

# Check if stack exists
Write-Host "📋 Checking if stack exists..." -ForegroundColor Yellow
try {
    aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION --output json | Out-Null
    Write-Host "♻️  Stack exists. Updating..." -ForegroundColor Yellow
    $OPERATION = "update-stack"
    $WAIT_OPERATION = "stack-update-complete"
} catch {
    Write-Host "🆕 Creating new stack..." -ForegroundColor Green
    $OPERATION = "create-stack"
    $WAIT_OPERATION = "stack-create-complete"
}
Write-Host ""

# Deploy stack
Write-Host "🔨 Deploying CloudFormation stack..." -ForegroundColor Cyan
Write-Host "   This will take 5-10 minutes..." -ForegroundColor Gray
Write-Host ""

try {
    aws cloudformation $OPERATION `
        --stack-name $STACK_NAME `
        --template-body file://$TEMPLATE_FILE `
        --parameters ParameterKey=KeyName,ParameterValue=$KEY_NAME `
        --region $REGION `
        --capabilities CAPABILITY_IAM `
        --output json | Out-Null
    
    # Wait for completion
    Write-Host "⏳ Waiting for deployment to complete..." -ForegroundColor Yellow
    aws cloudformation wait $WAIT_OPERATION `
        --stack-name $STACK_NAME `
        --region $REGION
    
    Write-Host ""
    Write-Host "✅ Deployment complete!" -ForegroundColor Green
    Write-Host ""
    
    # Get outputs
    Write-Host "📊 Stack Outputs:" -ForegroundColor Cyan
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    
    $outputs = aws cloudformation describe-stacks `
        --stack-name $STACK_NAME `
        --region $REGION `
        --query 'Stacks[0].Outputs' `
        --output json | ConvertFrom-Json
    
    $publicIP = ($outputs | Where-Object { $_.OutputKey -eq "PublicIP" }).OutputValue
    $publicDNS = ($outputs | Where-Object { $_.OutputKey -eq "PublicDNS" }).OutputValue
    $instanceId = ($outputs | Where-Object { $_.OutputKey -eq "InstanceId" }).OutputValue
    
    Write-Host "Instance ID:  $instanceId" -ForegroundColor White
    Write-Host "Public IP:    $publicIP" -ForegroundColor White
    Write-Host "Public DNS:   $publicDNS" -ForegroundColor White
    Write-Host ""
    Write-Host "🌐 Access URLs:" -ForegroundColor Green
    Write-Host "   Web UI:  http://$publicIP`:8000" -ForegroundColor White
    Write-Host "   API:     http://$publicIP`:8000/docs" -ForegroundColor White
    Write-Host "   Health:  http://$publicIP`:8000/health" -ForegroundColor White
    Write-Host ""
    Write-Host "🔌 SSH Access:" -ForegroundColor Green
    Write-Host "   ssh -i $KEY_NAME.pem ubuntu@$publicIP" -ForegroundColor White
    Write-Host ""
    Write-Host "📝 Note: Wait 2-3 minutes for the application to start" -ForegroundColor Yellow
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    
} catch {
    if ($OPERATION -eq "update-stack" -and $_.Exception.Message -like "*No updates*") {
        Write-Host "⚠️  No updates to perform (stack unchanged)" -ForegroundColor Yellow
    } else {
        Write-Host "❌ Deployment failed: $_" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "🎉 Deployment script completed!" -ForegroundColor Green
