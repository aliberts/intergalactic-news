data "aws_ecr_authorization_token" "token" {}

resource "aws_ecr_repository" "lambda_image_repo" {
  image_tag_mutability = "MUTABLE"
  name                 = "${var.project_name}-${var.stage}"
  tags                 = var.tags
  force_delete         = true
  encryption_configuration {
    encryption_type = "AES256"
  }
  image_scanning_configuration {
    scan_on_push = "false"
  }
  provisioner "local-exec" {
    # https://stackoverflow.com/a/74395215
    command = <<EOF
      export REPO_URL=${aws_ecr_repository.lambda_image_repo.repository_url}
      docker login ${data.aws_ecr_authorization_token.token.proxy_endpoint} \
          -u AWS -p ${data.aws_ecr_authorization_token.token.password}
      docker pull alpine
      docker image rm -rf $REPO_URL
      docker tag alpine $REPO_URL:dummy
      docker tag alpine $REPO_URL:latest
      docker push $REPO_URL --all-tags
      EOF
  }
}

data "aws_iam_policy_document" "lambda_image_repo_policy_document" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    actions = [
      "ecr:BatchGetImage",
      "ecr:DeleteRepositoryPolicy",
      "ecr:GetDownloadUrlForLayer",
      "ecr:GetRepositoryPolicy",
      "ecr:SetRepositoryPolicy"
    ]
    condition {
      test     = "StringLike"
      variable = "aws:sourceArn"
      values = [
        "arn:aws:lambda:${var.region}:${var.account_id}:function:*"
      ]
    }
  }
}

resource "aws_ecr_repository_policy" "lambda_image_repo_policy" {
  repository = aws_ecr_repository.lambda_image_repo.name
  policy     = data.aws_iam_policy_document.lambda_image_repo_policy_document.json
}
