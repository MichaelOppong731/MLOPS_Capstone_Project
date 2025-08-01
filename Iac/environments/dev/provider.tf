terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "6.5.0" # AWS provider version
    }
  }

  backend "s3" {
    bucket  = "mlopsnsp"
    key     = "dev/terraform.tfstate"
    region  = "eu-west-1"
    encrypt = true
  }
}
