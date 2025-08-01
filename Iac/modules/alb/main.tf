resource "aws_lb" "app_alb" {
  name               = "${var.environment}-${var.name}"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [var.alb_security_group_id]
  subnets            = var.public_subnet_ids

  enable_deletion_protection = false

  tags = {
    Name        = "${var.environment}-${var.name}"
    Environment = var.environment
  }
}

# HTTP Listener (no HTTPS redirect)
resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.app_alb.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app_tg.arn
  }
  
  depends_on = [aws_lb_target_group.app_tg]
}

# Target Group
resource "aws_lb_target_group" "app_tg" {
  name        = "${var.environment}-${var.target_group_name}"
  port        = var.target_group_port
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "ip"

  health_check {
    enabled             = true
    healthy_threshold   = 2
    interval            = 30
    matcher             = "200"
    path                = var.health_check_path
    port                = "traffic-port"
    protocol            = "HTTP"
    timeout             = 5
    unhealthy_threshold = 2
  }

  tags = {
    Name        = "${var.environment}-${var.target_group_name}"
    Environment = var.environment
  }
}