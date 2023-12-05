provider "aws" {
  region                   = var.region
  shared_credentials_files = ["~/.aws/credentials"]
}

module "ecr" {
  source       = "./modules/ecr"
  account_id   = var.account_id
  region       = var.region
  project_name = var.project_name
  stage        = var.stage
  tags         = local.tags
}

module "s3_bucket" {
  source      = "./modules/s3_bucket"
  bucket_name = "${var.project_name}-${var.stage}"
  tags        = local.tags
}

module "cloudwatch_logs" {
  source        = "./modules/cloudwatch_logs"
  function_name = "${var.project_name}-${var.stage}"
  tags          = local.tags
}

module "lambda" {
  source               = "./modules/lambda"
  account_id           = var.account_id
  region               = var.region
  project_name         = var.project_name
  stage                = var.stage
  lambda_log_group_arn = module.cloudwatch_logs.lambda_log_group_arn
  ecr_repo_url         = module.ecr.ecr_repo_url
  s3_bucket_arn        = module.s3_bucket.bucket_arn
  tags                 = local.tags
  google_api_key       = var.google_api_key
  mailchimp_api_key    = var.mailchimp_api_key
  openai_api_key       = var.openai_api_key
  depends_on = [
    module.ecr,
    module.s3_bucket,
    module.cloudwatch_logs
  ]
}

module "s3_bucket_policy" {
  source          = "./modules/s3_bucket_policy"
  bucket_name     = module.s3_bucket.bucket_id
  bucket_arn      = module.s3_bucket.bucket_arn
  lambda_role_arn = module.lambda.lambda_role_arn
  depends_on = [
    module.s3_bucket,
    module.lambda
  ]
}

module "eventbridge" {
  source              = "./modules/eventbridge"
  project_name        = var.project_name
  stage               = var.stage
  schedule_expression = var.schedule_expression
  tags                = local.tags
  lambda_arn          = module.lambda.lambda_function_arn
  event_file          = var.event_file
  depends_on          = [module.lambda]
}

module "lambda_permission" {
  source               = "./modules/lambda_permission"
  lambda_trigger_arn   = module.eventbridge.lambda_trigger_arn
  lambda_function_name = module.lambda.lambda_function_name
  depends_on = [
    module.lambda,
    module.eventbridge
  ]
}

data "terraform_remote_state" "setup" {
  backend = "local"
  config = {
    path = "./setup/terraform.tfstate"
  }
}

module "iam_github_role" {
  source              = "./modules/iam_github_role"
  project_name        = var.project_name
  stage               = var.stage
  github_repo_owner   = var.github_repo_owner
  github_repo_name    = var.github_repo_name
  github_idp_arn      = data.terraform_remote_state.setup.outputs.github_idp_arn
  lambda_function_arn = module.lambda.lambda_function_arn
  ecr_repo_arn        = module.ecr.ecr_repo_arn
  tags                = local.tags
  depends_on = [
    data.terraform_remote_state.setup,
    module.lambda,
    module.ecr
  ]
}
