variable "name" {
  type = string
}

variable "security_groups" {
  type = list(string)
}

variable "subnets" {
  type = list(string)
}

variable "vpc_id" {
  type = string
}

variable "target_group_name" {
  type = string
}

variable "target_group_port" {
  type = number
  default = 80
}

variable "health_check_path" {
  type    = string
  default = "/"
}

variable "environment" {
  description = "Environment name (e.g. dev, staging, prod)"
  type        = string
}

variable "alb_security_group_id" {
  description = "Security group ID for the ALB"
  type        = string
}

variable "public_subnet_ids" {
  description = "List of public subnet IDs for the ALB"
  type        = list(string)
}



