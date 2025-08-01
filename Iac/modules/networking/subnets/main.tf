# Create public subnets
resource "aws_subnet" "travel_itinerary_public_subnet" {
  count                   = length(var.cidr_public_subnet)
  vpc_id                  = var.vpc_id
  cidr_block              = element(var.cidr_public_subnet, count.index)
  availability_zone       = element(var.availability_zones, count.index)
  map_public_ip_on_launch = var.map_public_ip_on_launch

  tags = {
    Name        = "${var.environment}/travel-public-subnet-${count.index + 1}"
    Environment = var.environment
  }
}

# Create private subnets
resource "aws_subnet" "travel_itinerary_private_subnet" {
  count             = length(var.cidr_private_subnet)
  vpc_id            = var.vpc_id
  cidr_block        = element(var.cidr_private_subnet, count.index)
  availability_zone = element(var.availability_zones, count.index)

  tags = {
    Name        = "${var.environment}/travel-private-subnet-${count.index + 1}"
    Environment = var.environment
  }
} 

