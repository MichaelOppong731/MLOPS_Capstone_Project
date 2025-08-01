resource "aws_service_discovery_private_dns_namespace" "this" {
  name        = var.namespace
  description = "Service discovery namespace for ${var.environment} environment"
  vpc         = var.vpc_id

  tags = {
    Name        = "${var.environment}-${var.namespace}"
    Environment = var.environment
  }
}

resource "aws_service_discovery_service" "this" {
  for_each = var.services

  name = each.key

  dns_config {
    namespace_id = aws_service_discovery_private_dns_namespace.this.id

    dns_records {
      ttl  = 10
      type = "A"
    }

    routing_policy = "MULTIVALUE"
  }



  tags = {
    Name        = "${var.environment}-${each.key}"
    Environment = var.environment
  }

  lifecycle {
    create_before_destroy = true
  }
}
