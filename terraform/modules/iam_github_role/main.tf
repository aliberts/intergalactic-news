data "aws_iam_policy_document" "github_actions_assume_role" {
  statement {
    effect = "Allow"
    principals {
      type        = "Federated"
      identifiers = [var.github_idp_arn]
    }
    actions = ["sts:AssumeRoleWithWebIdentity"]
    condition {
      test     = "StringLike"
      variable = "token.actions.githubusercontent.com:aud"
      values = [
        "sts.amazonaws.com"
      ]
    }
    condition {
      test     = "StringLike"
      variable = "token.actions.githubusercontent.com:sub"
      values = [
        "repo:${var.github_repo_owner}/${var.github_repo_name}:*"
      ]
    }
  }
}

data "aws_iam_policy_document" "github_actions_ecr_push" {
  # from https://github.com/aws-actions/amazon-ecr-login#ecr-private
  statement {
    effect = "Allow"
    actions = [
      "ecr:GetAuthorizationToken"
    ]
    resources = [
      "*"
    ]
  }
  statement {
    effect = "Allow"
    actions = [
      "ecr:BatchGetImage",
      "ecr:BatchCheckLayerAvailability",
      "ecr:CompleteLayerUpload",
      "ecr:GetDownloadUrlForLayer",
      "ecr:InitiateLayerUpload",
      "ecr:PutImage",
      "ecr:UploadLayerPart"
    ]
    resources = [
      var.ecr_repo_arn
    ]
  }
}

data "aws_iam_policy_document" "github_actions_lambda_update" {
  statement {
    effect = "Allow"
    actions = [
      "lambda:UpdateFunctionCode"
    ]
    resources = [
      var.lambda_function_arn
    ]
  }
}

resource "aws_iam_role" "github_actions_role" {
  name                 = "${var.project_name}-${var.stage}-github-actions"
  description          = "IAM role for Github Actions to push image builds to ecr"
  max_session_duration = "3600"
  tags                 = var.tags
  assume_role_policy   = data.aws_iam_policy_document.github_actions_assume_role.json
  # managed_policy_arns  = ["arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryFullAccess"]
  inline_policy {
    name   = "github_actions_ecr_push"
    policy = data.aws_iam_policy_document.github_actions_ecr_push.json
  }
  inline_policy {
    name   = "github_actions_lambda_update"
    policy = data.aws_iam_policy_document.github_actions_lambda_update.json
  }
}
