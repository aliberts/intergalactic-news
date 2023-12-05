data "aws_iam_policy_document" "lambda_assume_role" {
  statement {
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
    actions = ["sts:AssumeRole"]
  }
}

data "aws_iam_policy_document" "lambda_s3_policy" {
  statement {
    effect = "Allow"
    actions = [
      "s3:*"
    ]
    resources = [
      var.s3_bucket_arn
    ]
  }
}

data "aws_iam_policy_document" "lambda_logs_policy" {
  statement {
    effect = "Allow"
    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = [
      "${var.lambda_log_group_arn}:*"
    ]
  }
}

resource "aws_iam_role" "lambda_role" {
  name               = "${var.project_name}-${var.stage}-lambda"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
  inline_policy {
    name   = "s3_policy"
    policy = data.aws_iam_policy_document.lambda_s3_policy.json
  }
  inline_policy {
    name   = "logs_policy"
    policy = data.aws_iam_policy_document.lambda_logs_policy.json
  }
}

resource "aws_lambda_function" "lambda" {
  function_name = "${var.project_name}-${var.stage}"
  role          = aws_iam_role.lambda_role.arn
  tags          = var.tags
  package_type  = "Image"
  image_uri     = "${var.ecr_repo_url}:latest"
  architectures = ["x86_64"]
  timeout       = 900
  memory_size   = 256 # Min 128 MB - Max 10240 MB
  ephemeral_storage {
    size = 512 # Min 512 MB - Max 10240 MB
  }
  environment {
    variables = {
      GOOGLE_API_KEY    = var.google_api_key
      MAILCHIMP_API_KEY = var.mailchimp_api_key
      OPENAI_API_KEY    = var.openai_api_key
    }
  }
}
