# CREATE ECS CLUSTER MODULE AND CAPACITY PROVIDERS
resource "aws_ecs_cluster" "micro_service_cluster" {
  name = "${var.environment}-${var.cluster_name}"
  setting {
    name  = "containerInsights"
    value = "disabled"
  }
}

# SPECIFY CAPACITY PROVIDERS FOR THE ECS CLUSTER
resource "aws_ecs_cluster_capacity_providers" "cluster_capacity_providers" {
  cluster_name = aws_ecs_cluster.micro_service_cluster.name

  capacity_providers = ["FARGATE", "FARGATE_SPOT"]

  default_capacity_provider_strategy {
    base              = 1
    weight            = 1
    capacity_provider = var.capacity_provider
  }
}
