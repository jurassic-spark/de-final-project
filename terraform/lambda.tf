resource "aws_s3_object" "ingest_function_zip" {
  bucket = aws_s3_bucket.code.id
  key    = "ingest_raw_data/ingest_function.zip"

  source = data.archive_file.ingest_function.output_path
}

resource "aws_lambda_function" "ingest_raw_data" {
  function_name = var.lambda_name
  s3_bucket     = aws_s3_bucket.code.bucket
  s3_key        = aws_s3_object.ingest_function_zip.key
  role          = aws_iam_role.extract_lambda_role.arn
  handler       = "placeholder_lambda.lambda_handler"
  depends_on    = [aws_cloudwatch_log_group.ingest_function_log_group]
  runtime       = "python3.13"
  logging_config {
    log_format = "Text"
    log_group  = aws_cloudwatch_log_group.ingest_function_log_group.name
  }
}

data "archive_file" "ingest_function" {
  type        = "zip"
  source_file = "${path.module}/../src/placeholder_lambda.py"
  output_path = "${path.module}/function.zip"
}