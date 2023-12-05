terraform {
  backend "s3" {
    # use `terraform init -backend-config=setup/backend.tfvars
    region         = ""
    bucket         = ""
    key            = ""
    dynamodb_table = ""
  }
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.29.0"
    }
  }
}
