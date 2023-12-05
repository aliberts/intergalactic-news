data "aws_iam_policy_document" "s3_policy" {

  statement {
    effect = "Allow"
    principals {
      type        = "AWS"
      identifiers = [var.lambda_role_arn]
    }
    actions = [
      "s3:*"
    ]
    resources = [
      var.bucket_arn,
      "${var.bucket_arn}/*"
    ]
  }
}

resource "aws_s3_bucket_policy" "allow_lambda_access" {
  bucket = var.bucket_name
  policy = data.aws_iam_policy_document.s3_policy.json
}
