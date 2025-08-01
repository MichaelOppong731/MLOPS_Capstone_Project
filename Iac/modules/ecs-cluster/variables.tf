variable "cluster_name" {
  description = "Base name for the ECS clusters"
  type        = string
}

variable "environment" {
  description = "Environment name (e.g. dev, staging, prod)"
  type        = string
}

variable "capacity_provider" {
  description = "Capacity provider to use (FARGATE or FARGATE_SPOT)"
  type        = string
  default     = "FARGATE"
  validation {
    condition     = contains(["FARGATE", "FARGATE_SPOT"], var.capacity_provider)
    error_message = "Capacity provider must be either FARGATE or FARGATE_SPOT."
  }
}
