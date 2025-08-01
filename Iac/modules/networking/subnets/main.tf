# Create public subnets
resource "aws_subnet" "house_price_public_subnet" {
  count                   = length(var.cidr_public_subnet)
  vpc_id                  = var.vpc_id
  cidr_block              = element(var.cidr_public_subnet, count.index)
  availability_zone       = element(var.availability_zones, count.index)
  map_public_ip_on_launch = var.map_public_ip_on_launch

  tags = {
    Name        = "${var.environment}-house-price-public-subnet-${count.index + 1}"
    Environment = var.environment
  }
}

# Create private subnets (kept for future use, but not using NAT gateway)
resource "aws_subnet" "house_price_private_subnet" {
  count             = length(var.cidr_private_subnet)
  vpc_id            = var.vpc_id
  cidr_block        = element(var.cidr_private_subnet, count.index)
  availability_zone = element(var.availability_zones, count.index)

  tags = {
    Name        = "${var.environment}-house-price-private-subnet-${count.index + 1}"
    Environment = var.environment
  }
} 

