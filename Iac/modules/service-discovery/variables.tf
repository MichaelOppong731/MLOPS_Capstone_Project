variable "namespace" {
  description = "Name of the service discovery namespace"
  type        = string
  default     = "services"
}

variable "vpc_id" {
  description = "ID of the VPC where the service discovery namespace will be created"
  type        = string
}

variable "environment" {
  description = "Environment name (e.g., dev, staging, prod)"
  type        = string
}

variable "services" {
  description = "Map of services to register with service discovery"
  type        = map(any)
  default     = {}
}