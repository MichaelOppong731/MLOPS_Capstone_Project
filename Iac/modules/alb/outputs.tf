output "alb_arn" {
  value = aws_lb.app_alb.arn
}

output "alb_dns_name" {
  description = "DNS name of the ALB"
  value       = aws_lb.app_alb.dns_name
}

output "target_group_arn" {
  description = "ARN of the target group"
  value       = aws_lb_target_group.app_tg.arn
}

output "alb_zone_id" {
  description = "Zone ID of the ALB"
  value       = aws_lb.app_alb.zone_id
}



output "http_listener_arn" {
  description = "ARN of the HTTP listener"  
  value       = aws_lb_listener.http.arn
}