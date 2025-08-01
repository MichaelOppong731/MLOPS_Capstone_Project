variable "project_name" {
  description = "A name prefix for all resources to help with identification."
  type        = string
}
variable "environment" {
  description = "Environment name (e.g. dev, staging, prod)"
  type        = string
}

variable "vpc_id" {
  description = "ID of the VPC where the security group will be created"
  type        = string
}

variable "vpc_cidr" {
  description = "CIDR block of the VPC"
  type        = string
}
