


resource "aws_cloudwatch_log_group" "ecs_log_group" {
  name              = "/ecs/${var.name}"
  retention_in_days = 1
}
# Create a task definition for the ECS service
resource "aws_ecs_task_definition" "micro_service_td" {
  family                   = var.family
  cpu                      = var.cpu
  memory                   = var.memory
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  execution_role_arn       = var.task_execution_role_arn
  task_role_arn            = var.task_execution_role_arn

  container_definitions = jsonencode([
    {
      name      = var.container_name
      image     = var.container_image
      portMappings = var.container_port != null ? [{
        containerPort = var.container_port
        hostPort      = var.container_port
      }] : []
      environment = var.environment
      secrets     = var.secrets
      stopTimeout = 120

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = var.log_group_name
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "ecs"
        }
      }
    }
  ])

  depends_on = [aws_cloudwatch_log_group.ecs_log_group]
}


resource "aws_ecs_service" "cluster_service" {
  name            = var.name
  cluster         = var.cluster_id
  task_definition = aws_ecs_task_definition.micro_service_td.arn
  desired_count   = var.desired_count
  enable_execute_command = true
  health_check_grace_period_seconds = var.health_check_grace_period_seconds

  deployment_maximum_percent         = 200
  deployment_minimum_healthy_percent = 100
  
  # Configure deployment circuit breaker
  # This will enable rollback on failure
  # and prevent the service from being left in a broken state
  deployment_circuit_breaker {
    enable   = true
    rollback = true
  }

  capacity_provider_strategy {
    capacity_provider = var.capacity_provider
    weight           = 1
    base             = 1
  }

  network_configuration {
    subnets         = var.subnets
    security_groups = var.security_groups
    assign_public_ip = var.assign_public_ip
  }

  dynamic "load_balancer" {
    for_each = var.enable_load_balancer ? [1] : []
    content {
      target_group_arn = var.target_group_arn
      container_name   = var.container_name
      container_port   = var.container_port
    }
  }

  dynamic "service_registries" {
    for_each = var.service_discovery_enabled ? [1] : []
    content {
      registry_arn = var.service_discovery_arn
      container_name = var.container_name
    }
  }

  depends_on = [
    aws_ecs_task_definition.micro_service_td
  ]
  
  # Add lifecycle rule to ensure target group is properly associated before service creation
  lifecycle {
    create_before_destroy = true
  }
}
