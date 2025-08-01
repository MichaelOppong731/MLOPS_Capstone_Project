output "public_route_table_id" {
  description = "ID of the public route table"
  value       = aws_route_table.travel_itinerary_public_route_table.id
}


output "all_route_table_ids" {
  description = "All route table IDs for VPC endpoints"
  value       = concat([aws_route_table.travel_itinerary_public_route_table.id], aws_route_table.travel_itinerary_private_route_table[*].id)
}

output "private_route_table_ids" {
  description = "IDs of the private route tables"
  value       = aws_route_table.travel_itinerary_private_route_table[*].id
} 