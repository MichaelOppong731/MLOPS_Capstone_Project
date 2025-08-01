output "namespace_id" {
  description = "ID of the service discovery namespace"
  value       = aws_service_discovery_private_dns_namespace.this.id
}

output "namespace_name" {
  description = "Name of the service discovery namespace"
  value       = aws_service_discovery_private_dns_namespace.this.name
}

output "service_registry_arns" {
  description = "ARNs of the service discovery services"
  value       = { for k, v in aws_service_discovery_service.this : k => v.arn }
}

output "service_discovery_dns" {
  description = "DNS names for the services"
  value       = { for k, v in aws_service_discovery_service.this : k => "${k}.${aws_service_discovery_private_dns_namespace.this.name}" }
}