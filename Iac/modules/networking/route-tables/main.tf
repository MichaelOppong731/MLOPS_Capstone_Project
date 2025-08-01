# Create public route table and attach it to the internet gateway
resource "aws_route_table" "travel_itinerary_public_route_table" {
  vpc_id = var.vpc_id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = var.internet_gateway_id
  }

  tags = {
    Name        = "${var.environment}-travel-public-rt"
    Environment = var.environment
  }
}

# Public Route Table and Public Subnet Association
resource "aws_route_table_association" "travel_itinerary_public_rt_subnet_association" {
  count          = length(var.public_subnet_ids)
  subnet_id      = var.public_subnet_ids[count.index]
  route_table_id = aws_route_table.travel_itinerary_public_route_table.id
}

# Create private route tables (one for each AZ, all using single NAT Gateway)
resource "aws_route_table" "travel_itinerary_private_route_table" {
  count  = length(var.private_subnet_ids)
  vpc_id = var.vpc_id

  dynamic "route" {
    for_each = var.nat_gateway_id != null ? [1] : []
    content {
      cidr_block     = "0.0.0.0/0"
      nat_gateway_id = var.nat_gateway_id
    }
  }

  tags = {
    Name        = "${var.environment}-private-rt-${count.index}"
    Environment = var.environment
  }
}

# Private Route Table and Private Subnet Association
resource "aws_route_table_association" "travel_itinerary_private_rt_subnet_association" {
  count          = length(var.private_subnet_ids)
  subnet_id      = var.private_subnet_ids[count.index]
  route_table_id = aws_route_table.travel_itinerary_private_route_table[count.index].id
} 