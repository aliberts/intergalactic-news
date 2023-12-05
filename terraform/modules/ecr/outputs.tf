output "ecr_repo_arn" {
  value = aws_ecr_repository.lambda_image_repo.arn
}

output "ecr_repo_url" {
  value = aws_ecr_repository.lambda_image_repo.repository_url
}
