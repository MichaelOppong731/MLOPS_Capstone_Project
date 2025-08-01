variable "name" { type = string }
variable "cluster_id" { type = string }

variable "family" { type = string }
variable "cpu" { type = string }
variable "memory" { type = string }

variable "container_name" { type = string }
variable "container_image" { type = string }
variable "container_port" {
  description = "Port exposed by the container"
  type        = number
  default     = null
}

variable "container_ports" {
  description = "List of ports exposed by the container"
  type        = list(number)
  default     = []
}

variable "subnets" { type = list(string) }
variable "security_groups" { type = list(string) }

variable "desired_count" { type = number }

variable "environment" {
  type    = list(map(string))
  default = []
}

variable "secrets" {
  type    = list(map(string))
  default = []
  description = "List of secrets to pass to the container"
}

variable "enable_load_balancer" {
  type    = bool
  default = false
}

variable "target_group_arn" {
  type    = string
  default = ""
}

variable "alb_listener_arn" {
  type        = string
  default     = ""
  description = "ARN of the ALB listener to ensure it's created before the ECS service"
}

variable "aws_region" {
  description = "AWS region for CloudWatch logging"
  type        = string
}

variable "log_group_name" {
  description = "CloudWatch Log Group name"
  type        = string
  default     = ""
}

variable "service_discovery_id" {
  description = "ID of the service discovery service to register with"
  type        = string
  default     = null
}

variable "health_check_grace_period_seconds" {
  description = "Grace period for health checks"
  type        = number
  default     = 0
}

variable "secret_name" {
  type        = string
  description = "The name of the existing secret"
  default     = ""
}

variable "service_discovery_enabled" {
  description = "Whether to enable service discovery"
  type        = bool
  default     = false
}

variable "service_discovery_namespace_id" {
  description = "ID of the service discovery namespace"
  type        = string
  default     = ""
}

variable "service_discovery_name" {
  description = "Name for the service discovery service"
  type        = string
  default     = ""
}

variable "service_discovery_arn" {
  description = "ARN of the service discovery service created in the service-discovery module"
  type        = string
  default     = ""
}

variable "capacity_provider" {
  description = "Capacity provider to use (FARGATE or FARGATE_SPOT)"
  type        = string
  default     = "FARGATE_SPOT"
  validation {
    condition     = contains(["FARGATE", "FARGATE_SPOT"], var.capacity_provider)
    error_message = "Capacity provider must be either FARGATE or FARGATE_SPOT."
  }
}

variable "task_execution_role_arn" {
  description = "ARN of the ECS task execution role"
  type        = string
}

variable "assign_public_ip" {
  description = "Assign public IP to ECS tasks"
  type        = bool
}

variable env {
  description = "Environment variables to pass to the container"
  type        = string
  default     = "dev"
}