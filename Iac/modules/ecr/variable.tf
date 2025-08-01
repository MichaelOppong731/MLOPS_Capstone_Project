variable "names" {
  description = "Name of the ECR repository"
  type        = list(string)
}

variable "environment" {
  description = "Environment for the ECR repository (e.g., dev, prod)"
  type        = string
}

variable "project_name" {
  description = "Name of the project for tagging purposes"
  type        = string
  
}
