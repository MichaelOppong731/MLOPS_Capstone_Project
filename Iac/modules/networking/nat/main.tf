# Create single elastic IP for NAT gateway
resource "aws_eip" "travel_itinerary_elastic_ip" {
  domain = "vpc"
  tags = {
    Name        = "${var.environment}-travel-nat-eip"
    Environment = var.environment
  }
}

# Create single NAT gateway in first AZ
resource "aws_nat_gateway" "travel_itinerary_nat_gateway" {
  allocation_id = aws_eip.travel_itinerary_elastic_ip.id
  subnet_id     = var.public_subnet_ids[0]

  tags = {
    Name        = "${var.environment}-travel-nat-gateway"
    Environment = var.environment
  }

  depends_on = [aws_eip.travel_itinerary_elastic_ip]
} 