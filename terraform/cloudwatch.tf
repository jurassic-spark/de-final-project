resource "aws_cloudwatch_log_group" "ingest_function_log_group" {
  name              = "/aws/lambda/ingest_function_log"
  retention_in_days = 30
  lifecycle {
    prevent_destroy = false
  }
}