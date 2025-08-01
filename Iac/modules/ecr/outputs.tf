output "repository_urls" {
  description = "The URLs of the ECR repositories"
  value       = { for k, v in aws_ecr_repository.travel_itenerary_repo : k => v.repository_url }
}

output "repository_arns" {
  description = "The ARNs of the ECR repositories"
  value       = { for k, v in aws_ecr_repository.travel_itenerary_repo : k => v.arn }
}
