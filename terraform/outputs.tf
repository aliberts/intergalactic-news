output "ecr_repo_url" {
  value = module.ecr.ecr_repo_url
}

output "s3_bucket_arn" {
  value = module.s3_bucket.bucket_arn
}

output "lambda_function_arn" {
  value = module.lambda.lambda_function_arn
}

output "github_actions_role_arn" {
  value = module.iam_github_role.github_actions_role_arn
}
