# Create VPC
resource "aws_vpc" "house_price_vpc" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name        = "${var.environment}-house-price-vpc"
    Environment = var.environment
  }
}

# Create internet gateway
resource "aws_internet_gateway" "house_price_internet_gateway" {
  vpc_id = aws_vpc.house_price_vpc.id

  tags = {
    Name        = "${var.environment}-house-price-igw"
    Environment = var.environment
  }
} 