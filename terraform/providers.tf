terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.20"
    }
  }
}
provider "aws" {
  region = "eu-west-2"
  default_tags {
    tags = {
      ProjectName  = "de-final-project"
      Team         = "Jurassic Sparks"
      DeployedFrom = "Terraform"
      Repository   = "de-final-project"
      CostCentre   = "DE"
      Environment  = "dev"
    }
  }
}
