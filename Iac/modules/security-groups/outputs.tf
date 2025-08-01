output "alb_sg_id" {
  description = "Security group ID for the ALB"
  value       = aws_security_group.alb_sg.id
}

output "ecs_tasks_sg_id" {
  description = "Security group ID for ECS tasks"
  value       = aws_security_group.ecs_tasks_sg.id
}