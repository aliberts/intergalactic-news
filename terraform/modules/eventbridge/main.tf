resource "aws_cloudwatch_event_rule" "lambda_trigger_event" {
  description         = "daily schedule trigger"
  event_bus_name      = "default"
  name                = "${var.project_name}-${var.stage}_lambda-trigger"
  schedule_expression = var.schedule_expression
  tags                = var.tags
}

resource "aws_cloudwatch_event_target" "lambda_trigger_event_target" {
  rule  = aws_cloudwatch_event_rule.lambda_trigger_event.name
  arn   = var.lambda_arn
  input = file("${path.root}/../events/${var.event_file}")
}
