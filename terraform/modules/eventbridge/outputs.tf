output "lambda_trigger_arn" {
  value = aws_cloudwatch_event_rule.lambda_trigger_event.arn
}

output "lambda_trigger_name" {
  value = aws_cloudwatch_event_rule.lambda_trigger_event.name
}
