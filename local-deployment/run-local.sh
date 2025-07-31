#!/bin/bash

# Script to run House Price Predictor from ECR images locally
# This script handles ECR authentication and starts the services

set -e

# Configuration
AWS_PROFILE="mlops-profile"
AWS_REGION="eu-west-1"
ECR_REPOSITORY_API="house-price-api"
ECR_REPOSITORY_UI="house-price-ui"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BLUE}🏠 House Price Predictor - Local Deployment${NC}"
echo "=============================================="

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI is not installed. Please install it first.${NC}"
    echo "Install with: pip install awscli"
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo -e "${RED}❌ Docker is not running. Please start Docker first.${NC}"
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ docker-compose is not installed. Please install it first.${NC}"
    exit 1
fi

# Get AWS account ID
echo -e "${YELLOW}🔍 Getting AWS account ID...${NC}"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --profile $AWS_PROFILE --query Account --output text 2>/dev/null)
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to get AWS account ID. Check your AWS credentials for profile: $AWS_PROFILE${NC}"
    echo "Run: aws configure --profile $AWS_PROFILE"
    exit 1
fi

# Construct ECR registry URL
ECR_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
echo -e "${GREEN}✅ ECR Registry: ${ECR_REGISTRY}${NC}"

# Login to ECR
echo -e "${YELLOW}🔐 Logging in to ECR...${NC}"
aws ecr get-login-password --profile $AWS_PROFILE --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REGISTRY
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to login to ECR. Check your permissions for profile: $AWS_PROFILE${NC}"
    exit 1
fi

# Export ECR_REGISTRY for docker-compose
export ECR_REGISTRY

# Create .env file for docker-compose
echo "ECR_REGISTRY=${ECR_REGISTRY}" > .env

# Pull the latest images
echo -e "${YELLOW}📥 Pulling latest images...${NC}"
echo "API Image: ${ECR_REGISTRY}/${ECR_REPOSITORY_API}:latest"
docker pull ${ECR_REGISTRY}/${ECR_REPOSITORY_API}:latest
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to pull API image. Check if it exists in ECR.${NC}"
    exit 1
fi

echo "UI Image: ${ECR_REGISTRY}/${ECR_REPOSITORY_UI}:latest"
docker pull ${ECR_REGISTRY}/${ECR_REPOSITORY_UI}:latest
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to pull UI image. Check if it exists in ECR.${NC}"
    exit 1
fi

# Stop any existing containers
echo -e "${YELLOW}🛑 Stopping any existing containers...${NC}"
docker-compose down 2>/dev/null || true

# Start the services
echo -e "${YELLOW}🚀 Starting House Price Predictor services...${NC}"
docker-compose up -d

# Wait for services to be ready
echo -e "${YELLOW}⏳ Waiting for services to start...${NC}"
sleep 15

# Check API health
echo -e "${YELLOW}🔍 Checking API health...${NC}"
for i in {1..10}; do
    if curl -f http://localhost:8000/health >/dev/null 2>&1; then
        echo -e "${GREEN}✅ API is healthy!${NC}"
        break
    else
        if [ $i -eq 10 ]; then
            echo -e "${RED}❌ API health check failed after 10 attempts${NC}"
            echo -e "${YELLOW}📋 API logs:${NC}"
            docker-compose logs api
            exit 1
        fi
        echo "Attempt $i/10: API not ready yet, waiting..."
        sleep 3
    fi
done

# Test API prediction
echo -e "${YELLOW}🔍 Testing API prediction...${NC}"
PREDICTION_RESPONSE=$(curl -s -X POST "http://localhost:8000/predict" \
    -H "Content-Type: application/json" \
    -d '{
        "sqft": 1500,
        "bedrooms": 3,
        "bathrooms": 2,
        "location": "suburban",
        "year_built": 2000,
        "condition": "fair"
    }')

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ API prediction test passed!${NC}"
    echo -e "${CYAN}📊 Sample prediction: ${PREDICTION_RESPONSE}${NC}"
else
    echo -e "${RED}❌ API prediction test failed!${NC}"
    exit 1
fi

# Check UI accessibility
echo -e "${YELLOW}🔍 Checking UI accessibility...${NC}"
for i in {1..5}; do
    if curl -f http://localhost:8501 >/dev/null 2>&1; then
        echo -e "${GREEN}✅ UI is accessible!${NC}"
        break
    else
        if [ $i -eq 5 ]; then
            echo -e "${YELLOW}⚠️  UI might still be starting up${NC}"
            break
        fi
        echo "Attempt $i/5: UI not ready yet, waiting..."
        sleep 5
    fi
done

echo ""
echo -e "${GREEN}🎉 House Price Predictor is running successfully!${NC}"
echo ""
echo -e "${BLUE}📋 Services:${NC}"
echo -e "  🔗 ${CYAN}API:${NC}          http://localhost:8000"
echo -e "  🔗 ${CYAN}API Health:${NC}   http://localhost:8000/health"
echo -e "  🔗 ${CYAN}API Docs:${NC}     http://localhost:8000/docs"
echo -e "  🎨 ${CYAN}UI:${NC}           http://localhost:8501"
echo ""
echo -e "${BLUE}🤖 Model Information:${NC}"
echo -e "  📊 ${CYAN}Algorithm:${NC}    LinearRegression"
echo -e "  📈 ${CYAN}R² Score:${NC}     0.9901 (99.01% accuracy)"
echo -e "  🎯 ${CYAN}Features:${NC}     10 selected features (RFE)"
echo ""
echo -e "${YELLOW}💡 Commands:${NC}"
echo -e "  📋 View logs:     ${CYAN}docker-compose logs -f${NC}"
echo -e "  🛑 Stop services: ${CYAN}docker-compose down${NC}"
echo -e "  🔄 Restart:       ${CYAN}./run-local.sh${NC}"
echo ""
echo -e "${GREEN}✨ Your MLOps pipeline is complete! From Databricks MLflow to local deployment.${NC}"