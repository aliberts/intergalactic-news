resource "aws_lambda_permission" "lambda_trigger_allow" {
  action        = "lambda:InvokeFunction"
  function_name = var.lambda_function_name
  principal     = "events.amazonaws.com"
  source_arn    = var.lambda_trigger_arn
  statement_id  = "AWSEvents_${var.lambda_function_name}-trigger"
}
