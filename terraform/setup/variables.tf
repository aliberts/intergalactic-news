variable "region" {
  description = "AWS Region"
  type        = string
}

variable "bucket" {
  description = "Backend Bucket Name"
  type        = string
}

variable "dynamodb_table" {
  description = "Backend DynamoDB Name"
  type        = string
}

variable "key" {}
