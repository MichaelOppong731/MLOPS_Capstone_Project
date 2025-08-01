# This module creates an AWS ECR repository with a lifecycle policy to manage image retention.
# It allows for mutable image tags and prevents the repository from being destroyed.
resource "aws_ecr_repository" "travel_itenerary_repo" {
  for_each = toset(var.names)
  name                 = "${var.environment}/${each.value}"
  image_tag_mutability = "MUTABLE"

  tags = {
    Project = var.project_name
    Environment     = var.environment
  }

  lifecycle {
    prevent_destroy = true
    ignore_changes = [
      tags,
      image_tag_mutability,
      name
    ]
  }
}

# This resource sets a lifecycle policy for the ECR repository to expire untagged images older than 14 days.
# It uses a JSON policy format to define the rules for image selection and action.
resource "aws_ecr_lifecycle_policy" "ecr_repo_policy" {
  for_each = aws_ecr_repository.travel_itenerary_repo
  repository = each.value.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Expire untagged images older than 14 days"
        selection = {
          tagStatus     = "untagged"
          countType     = "sinceImagePushed"
          countUnit     = "days"
          countNumber   = 14
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}
