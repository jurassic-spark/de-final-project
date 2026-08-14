resource "aws_s3_object" "ingest_function_zip" {
  bucket = aws_s3_bucket.code.id
  key    = "ingest_raw_data/ingest_function.zip"

  source      = data.archive_file.ingest_function.output_path
  source_hash = data.archive_file.ingest_function.output_base64sha256
}

resource "aws_s3_object" "lambda_layer_zip" {
  bucket = aws_s3_bucket.code.id
  key    = "layers/ingest_function_layer.zip"

  source      = data.archive_file.lambda_layer.output_path
  source_hash = data.archive_file.lambda_layer.output_base64sha256
}

resource "aws_lambda_function" "ingest_raw_data" {
  function_name = var.lambda_name
  s3_bucket     = aws_s3_bucket.code.bucket
  s3_key        = aws_s3_object.ingest_function_zip.key

  role          = aws_iam_role.extract_lambda_role.arn
  handler       = "extract_data.lambda_handler"
  depends_on    = [aws_cloudwatch_log_group.ingest_function_log_group]
  runtime       = "python3.13"
  architectures = ["x86_64"]

  timeout     = 30
  memory_size = 1024

  source_code_hash = data.archive_file.ingest_function.output_base64sha256

  layers = [
    aws_lambda_layer_version.lambda_layer.arn,
    "arn:aws:lambda:eu-west-2:336392948345:layer:AWSSDKPandas-Python313:14"
  ]

  environment {
    variables = {
      INGEST_BUCKET = aws_s3_bucket.ingestion_zone.id
    }
  }
}

data "archive_file" "ingest_function" {
  type        = "zip"
  source_file = "${path.module}/../ingestion/extract_data.py"
  output_path = "${path.module}/function.zip"
}

resource "aws_lambda_layer_version" "lambda_layer" {
  s3_bucket = aws_s3_bucket.code.id
  s3_key    = aws_s3_object.lambda_layer_zip.key

  source_code_hash = data.archive_file.lambda_layer.output_base64sha256

  layer_name          = "ingest_function_layer"
  compatible_runtimes = ["python3.13"]
}

data "archive_file" "lambda_layer" {
  type        = "zip"
  source_dir  = "${path.module}/../lambda_layer"
  output_path = "${path.module}/lambda_layer.zip"
}