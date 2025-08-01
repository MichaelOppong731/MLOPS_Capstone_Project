output "public_subnet_ids" {
  description = "IDs of the public subnets"
  value       = aws_subnet.travel_itinerary_public_subnet[*].id
}

output "private_subnet_ids" {
  description = "IDs of the private subnets"
  value       = aws_subnet.travel_itinerary_private_subnet[*].id
}

output "public_subnet_cidrs" {
  description = "CIDR blocks of the public subnets"
  value       = aws_subnet.travel_itinerary_public_subnet[*].cidr_block
}

output "private_subnet_cidrs" {
  description = "CIDR blocks of the private subnets"
  value       = aws_subnet.travel_itinerary_private_subnet[*].cidr_block
} 