#!/bin/bash

# Script to test ECR images locally
# This script pulls images from your private ECR and runs them locally

set -e

# Configuration
AWS_REGION="eu-west-1"
ECR_REPOSITORY_API="house-price-api"
ECR_REPOSITORY_UI="house-price-ui"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🐳 Testing House Price Predictor ECR Images Locally${NC}"
echo "=================================================="

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI is not installed. Please install it first.${NC}"
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo -e "${RED}❌ Docker is not running. Please start Docker first.${NC}"
    exit 1
fi

# Get AWS account ID
echo -e "${YELLOW}🔍 Getting AWS account ID...${NC}"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to get AWS account ID. Check your AWS credentials.${NC}"
    exit 1
fi

# Construct ECR registry URL
ECR_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
echo -e "${GREEN}✅ ECR Registry: ${ECR_REGISTRY}${NC}"

# Login to ECR
echo -e "${YELLOW}🔐 Logging in to ECR...${NC}"
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REGISTRY
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to login to ECR. Check your permissions.${NC}"
    exit 1
fi

# Pull the latest images
echo -e "${YELLOW}📥 Pulling API image...${NC}"
docker pull ${ECR_REGISTRY}/${ECR_REPOSITORY_API}:latest
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to pull API image. Check if it exists in ECR.${NC}"
    exit 1
fi

echo -e "${YELLOW}📥 Pulling UI image...${NC}"
docker pull ${ECR_REGISTRY}/${ECR_REPOSITORY_UI}:latest
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to pull UI image. Check if it exists in ECR.${NC}"
    exit 1
fi

# Set environment variable for docker-compose
export ECR_REGISTRY

# Stop any existing containers
echo -e "${YELLOW}🛑 Stopping any existing containers...${NC}"
docker-compose -f docker-compose.local-test.yml down 2>/dev/null || true

# Start the services
echo -e "${YELLOW}🚀 Starting services...${NC}"
docker-compose -f docker-compose.local-test.yml up -d

# Wait for services to be ready
echo -e "${YELLOW}⏳ Waiting for services to be ready...${NC}"
sleep 30

# Test API health
echo -e "${YELLOW}🔍 Testing API health...${NC}"
if curl -f http://localhost:8000/health; then
    echo -e "${GREEN}✅ API health check passed!${NC}"
else
    echo -e "${RED}❌ API health check failed!${NC}"
    echo -e "${YELLOW}📋 API logs:${NC}"
    docker-compose -f docker-compose.local-test.yml logs api
    exit 1
fi

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
    echo -e "${BLUE}📊 Prediction response: ${PREDICTION_RESPONSE}${NC}"
else
    echo -e "${RED}❌ API prediction test failed!${NC}"
    exit 1
fi

# Test UI accessibility
echo -e "${YELLOW}🔍 Testing UI accessibility...${NC}"
if curl -f http://localhost:8501 >/dev/null 2>&1; then
    echo -e "${GREEN}✅ UI accessibility test passed!${NC}"
else
    echo -e "${RED}❌ UI accessibility test failed!${NC}"
    echo -e "${YELLOW}📋 UI logs:${NC}"
    docker-compose -f docker-compose.local-test.yml logs ui
    exit 1
fi

echo ""
echo -e "${GREEN}🎉 All tests passed! Your ECR images are working correctly.${NC}"
echo ""
echo -e "${BLUE}📋 Services running:${NC}"
echo -e "  🔗 API: http://localhost:8000"
echo -e "  🔗 API Health: http://localhost:8000/health"
echo -e "  🔗 API Docs: http://localhost:8000/docs"
echo -e "  🎨 UI: http://localhost:8501"
echo ""
echo -e "${YELLOW}💡 To stop the services, run:${NC}"
echo -e "  docker-compose -f docker-compose.local-test.yml down"
echo ""
echo -e "${YELLOW}📋 To view logs, run:${NC}"
echo -e "  docker-compose -f docker-compose.local-test.yml logs -f"