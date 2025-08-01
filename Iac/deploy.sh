#!/bin/bash

# House Price Predictor Infrastructure Deployment Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🏗️  House Price Predictor Infrastructure Deployment${NC}"
echo "=================================================="

# Configuration
ENVIRONMENT="dev"
AWS_REGION="eu-west-1"
AWS_ACCOUNT_ID="495599742316"

# Check prerequisites
echo -e "${YELLOW}🔍 Checking prerequisites...${NC}"

if ! command -v terraform &> /dev/null; then
    echo -e "${RED}❌ Terraform is not installed${NC}"
    echo "Install from: https://www.terraform.io/downloads.html"
    exit 1
fi

if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI is not installed${NC}"
    echo "Install from: https://aws.amazon.com/cli/"
    exit 1
fi

# Check AWS credentials
echo -e "${YELLOW}🔐 Checking AWS credentials...${NC}"
if ! aws sts get-caller-identity --profile mlops-profile &> /dev/null; then
    echo -e "${RED}❌ AWS credentials not configured for mlops-profile${NC}"
    echo "Run: aws configure --profile mlops-profile"
    exit 1
fi

# Set AWS profile
export AWS_PROFILE=mlops-profile

echo -e "${GREEN}✅ Prerequisites check passed${NC}"

# Navigate to environment directory
cd environments/${ENVIRONMENT}

# Initialize Terraform (skip backend for now)
echo -e "${YELLOW}🔧 Initializing Terraform...${NC}"
terraform init -backend=false

# Validate configuration
echo -e "${YELLOW}🔍 Validating Terraform configuration...${NC}"
terraform validate

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Terraform validation failed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Terraform validation passed${NC}"

# Plan deployment
echo -e "${YELLOW}📋 Creating deployment plan...${NC}"
terraform plan -var="aws_account_id=${AWS_ACCOUNT_ID}" -out=tfplan

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Terraform plan failed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Deployment plan created${NC}"

# Ask for confirmation
echo ""
echo -e "${YELLOW}⚠️  Ready to deploy infrastructure. This will create:${NC}"
echo "  • VPC with public/private subnets"
echo "  • ECS Fargate cluster"
echo "  • Application Load Balancer"
echo "  • Security Groups"
echo "  • IAM roles"
echo "  • Service Discovery"
echo ""
read -p "Do you want to proceed with deployment? (y/N): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}⏸️  Deployment cancelled${NC}"
    exit 0
fi

# Apply deployment
echo -e "${YELLOW}🚀 Deploying infrastructure...${NC}"
terraform apply tfplan

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}🎉 Infrastructure deployed successfully!${NC}"
    echo ""
    echo -e "${BLUE}📋 Deployment Summary:${NC}"
    echo "  • Environment: ${ENVIRONMENT}"
    echo "  • Region: ${AWS_REGION}"
    echo "  • Account: ${AWS_ACCOUNT_ID}"
    echo ""
    echo -e "${BLUE}🔗 Outputs:${NC}"
    terraform output
    echo ""
    echo -e "${YELLOW}💡 Next Steps:${NC}"
    echo "  1. Push your Docker images to ECR (GitHub Actions will do this)"
    echo "  2. ECS services will automatically pull and deploy the images"
    echo "  3. Access your UI via the ALB DNS name shown above"
    echo ""
    echo -e "${GREEN}✨ Your MLOps infrastructure is ready!${NC}"
else
    echo -e "${RED}❌ Infrastructure deployment failed${NC}"
    exit 1
fi