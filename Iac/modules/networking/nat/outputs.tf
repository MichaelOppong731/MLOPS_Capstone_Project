output "nat_gateway_id" {
  description = "ID of the NAT gateway"
  value       = aws_nat_gateway.travel_itinerary_nat_gateway.id
}

output "elastic_ip_id" {
  description = "ID of the Elastic IP"
  value       = aws_eip.travel_itinerary_elastic_ip.id
} 