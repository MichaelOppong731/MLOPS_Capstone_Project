# Create VPC
resource "aws_vpc" "travel_itinerary_vpc" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name        = "${var.environment}/travel-itinerary-vpc"
    Environment = var.environment
  }

  # lifecycle {
  #   prevent_destroy = true
  # }
}

# Create internet gateway
resource "aws_internet_gateway" "travel_itinerary_internet_gateway" {
  vpc_id = aws_vpc.travel_itinerary_vpc.id

  tags = {
    Name        = "${var.environment}-travel-igw"
    Environment = var.environment
  }
} 