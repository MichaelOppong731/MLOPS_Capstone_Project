output "cluster_id" {
  value = aws_ecs_cluster.micro_service_cluster.id
}

output "cluster_arn" {
  value = aws_ecs_cluster.micro_service_cluster.arn
}

output "capacity_providers" {
  value = aws_ecs_cluster_capacity_providers.cluster_capacity_providers.capacity_providers
}
