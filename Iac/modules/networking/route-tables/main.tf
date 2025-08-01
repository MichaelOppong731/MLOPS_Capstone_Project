# Create public route table and attach it to the internet gateway
resource "aws_route_table" "house_price_public_route_table" {
  vpc_id = var.vpc_id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = var.internet_gateway_id
  }

  tags = {
    Name        = "${var.environment}-house-price-public-rt"
    Environment = var.environment
  }
}

# Public Route Table and Public Subnet Association
resource "aws_route_table_association" "house_price_public_rt_subnet_association" {
  count          = length(var.public_subnet_ids)
  subnet_id      = var.public_subnet_ids[count.index]
  route_table_id = aws_route_table.house_price_public_route_table.id
}

# Create private route tables (no NAT gateway - simplified for stateful app)
resource "aws_route_table" "house_price_private_route_table" {
  count  = length(var.private_subnet_ids)
  vpc_id = var.vpc_id

  # No default route for private subnets since we're not using NAT gateway
  # Private subnets are kept for future use but isolated

  tags = {
    Name        = "${var.environment}-house-price-private-rt-${count.index + 1}"
    Environment = var.environment
  }
}

# Private Route Table and Private Subnet Association
resource "aws_route_table_association" "house_price_private_rt_subnet_association" {
  count          = length(var.private_subnet_ids)
  subnet_id      = var.private_subnet_ids[count.index]
  route_table_id = aws_route_table.house_price_private_route_table[count.index].id
} 