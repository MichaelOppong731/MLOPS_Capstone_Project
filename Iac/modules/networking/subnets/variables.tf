variable "vpc_id" {
  description = "ID of the VPC"
  type        = string
}

variable "environment" {
  description = "Environment name (e.g., dev, prod)"
  type        = string
}

variable "cidr_public_subnet" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
}

variable "cidr_private_subnet" {
  description = "CIDR blocks for private subnets"
  type        = list(string)
}

variable "availability_zones" {
  description = "List of availability zones"
  type        = list(string)
}

variable "map_public_ip_on_launch" {
  description = "Whether to automatically assign public IP addresses to instances launched in public subnets"
  type        = bool
  default     = true
} 