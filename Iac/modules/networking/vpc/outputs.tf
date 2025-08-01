output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.travel_itinerary_vpc.id
}

output "vpc_cidr" {
  description = "CIDR block of the VPC"
  value       = aws_vpc.travel_itinerary_vpc.cidr_block
}

output "internet_gateway_id" {
  description = "ID of the Internet Gateway"
  value       = aws_internet_gateway.travel_itinerary_internet_gateway.id
} 