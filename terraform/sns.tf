resource "aws_sns_topic" "error_notification" {
  name = "ingest_function_error_notification"
}

resource "aws_sns_topic_subscription" "ingest_function_error_email_subscription" {
  for_each = var.notification_emails
  topic_arn = aws_sns_topic.error_notification.arn
  protocol  = "email"
  endpoint  = each.value
}