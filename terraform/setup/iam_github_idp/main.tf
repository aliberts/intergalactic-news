data "tls_certificate" "github" {
  # https://stackoverflow.com/a/76603055
  url = "https://token.actions.githubusercontent.com/.well-known/openid-configuration"
}

resource "aws_iam_openid_connect_provider" "github" {
  url             = "https://token.actions.githubusercontent.com"
  thumbprint_list = [data.tls_certificate.github.certificates[0].sha1_fingerprint]
  client_id_list  = ["sts.amazonaws.com"]
  lifecycle {
    prevent_destroy = false
    # prevent_destroy = true
  }
}
