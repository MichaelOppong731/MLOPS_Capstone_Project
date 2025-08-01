provider "aws" {
  region = var.aws_region
}

# VPC Networking
module "vpc" {
  source = "../../modules/networking/vpc"

  vpc_cidr    = var.vpc_cidr
  environment = var.environment
}

module "subnets" {
  source = "../../modules/networking/subnets"

  vpc_id                  = module.vpc.vpc_id
  environment             = var.environment
  cidr_public_subnet      = var.cidr_public_subnet
  cidr_private_subnet     = var.cidr_private_subnet
  availability_zones      = var.availability_zones
  map_public_ip_on_launch = true
}

module "route_tables" {
  source = "../../modules/networking/route-tables"

  vpc_id              = module.vpc.vpc_id
  environment         = var.environment
  internet_gateway_id = module.vpc.internet_gateway_id
  public_subnet_ids   = module.subnets.public_subnet_ids
  private_subnet_ids  = module.subnets.private_subnet_ids
  nat_gateway_id      = null  # No NAT gateway needed
}

# IAM Roles
module "iam" {
  source = "../../modules/iam"

  environment  = var.environment
  project_name = var.project_name
}

# Security Groups
module "security_groups" {
  source = "../../modules/security-groups"

  vpc_id       = module.vpc.vpc_id
  vpc_cidr     = var.vpc_cidr
  environment  = var.environment
  project_name = var.project_name
}

# ECS Cluster
module "ecs_cluster" {
  source = "../../modules/ecs-cluster"

  cluster_name      = var.cluster_name
  environment       = var.environment
  capacity_provider = var.capacity_provider
}

# Service Discovery
module "service_discovery" {
  source = "../../modules/service-discovery"

  namespace   = "${var.project_name}-services"
  vpc_id      = module.vpc.vpc_id
  environment = var.environment

  services = {
    "inference-api" = {}
    "ui"           = {}
  }
}

# ALB for UI
module "ui_alb" {
  source = "../../modules/alb"

  name                  = "ui-alb"
  environment           = var.environment
  vpc_id                = module.vpc.vpc_id
  security_groups       = [module.security_groups.alb_sg_id]
  subnets               = module.subnets.public_subnet_ids
  target_group_name     = "ui-tg"
  target_group_port     = 8501
  health_check_path     = "/"
  alb_security_group_id = module.security_groups.alb_sg_id
  public_subnet_ids     = module.subnets.public_subnet_ids
}

# Inference API Service
module "inference_api_service" {
  source = "../../modules/ecs-service"

  name                    = "inference-api"
  cluster_id              = module.ecs_cluster.cluster_id
  task_execution_role_arn = module.iam.ecs_task_execution_role_arn
  capacity_provider       = var.capacity_provider
  family                  = "inference-api"
  cpu                     = "512"
  memory                  = "1024"
  container_name          = "inference-api"
  container_image         = "${var.aws_account_id}.dkr.ecr.${var.aws_region}.amazonaws.com/house-price-api:latest"
  container_port          = 8000
  subnets                 = module.subnets.public_subnet_ids
  assign_public_ip        = true
  security_groups         = [module.security_groups.ecs_tasks_sg_id]
  desired_count           = 1
  environment             = []
  env                     = var.environment
  enable_load_balancer    = false
  aws_region              = var.aws_region
  log_group_name          = "/ecs/inference-api"

  service_discovery_enabled      = true
  service_discovery_namespace_id = module.service_discovery.namespace_id
  service_discovery_name         = "inference-api"
  service_discovery_arn          = module.service_discovery.service_registry_arns["inference-api"]

  depends_on = [module.service_discovery]
}

# UI Service
module "ui_service" {
  source = "../../modules/ecs-service"

  name                    = "ui"
  cluster_id              = module.ecs_cluster.cluster_id
  task_execution_role_arn = module.iam.ecs_task_execution_role_arn
  capacity_provider       = var.capacity_provider
  family                  = "ui"
  cpu                     = "256"
  memory                  = "512"
  container_name          = "ui"
  container_image         = "${var.aws_account_id}.dkr.ecr.${var.aws_region}.amazonaws.com/house-price-ui:latest"
  container_port          = 8501
  subnets                 = module.subnets.public_subnet_ids
  assign_public_ip        = true
  security_groups         = [module.security_groups.ecs_tasks_sg_id]
  desired_count           = 1
  environment = [
    {
      name  = "API_URL"
      value = "http://inference-api.${var.project_name}-services:8000"
    }
  ]
  env                  = var.environment
  enable_load_balancer = true
  target_group_arn     = module.ui_alb.target_group_arn
  aws_region           = var.aws_region
  log_group_name       = "/ecs/ui"

  service_discovery_enabled      = true
  service_discovery_namespace_id = module.service_discovery.namespace_id
  service_discovery_name         = "ui"
  service_discovery_arn          = module.service_discovery.service_registry_arns["ui"]

  depends_on = [module.service_discovery, module.inference_api_service]
}

