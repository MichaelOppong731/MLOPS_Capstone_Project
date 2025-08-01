output "vpc_id" {
  description = "ID of the VPC"
  value       = module.vpc.vpc_id
}

output "ui_alb_dns_name" {
  description = "DNS name of the UI load balancer"
  value       = module.ui_alb.alb_dns_name
}

output "ui_alb_zone_id" {
  description = "Zone ID of the UI load balancer"
  value       = module.ui_alb.alb_zone_id
}

output "service_discovery_namespace" {
  description = "Service discovery namespace for internal communication"
  value       = "${var.project_name}-services"
}

output "inference_api_service_name" {
  description = "Service discovery name for inference API"
  value       = "inference-api.${var.project_name}-services"
}