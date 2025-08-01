variable "environment" {
  description = "Environment name (e.g., dev, prod)"
  type        = string
}

variable "availability_zones" {
  description = "List of availability zones"
  type        = list(string)
}

variable "public_subnet_ids" {
  description = "List of public subnet IDs where NAT gateways will be created"
  type        = list(string)
} 