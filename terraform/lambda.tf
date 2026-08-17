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

  role       = aws_iam_role.extract_lambda_role.arn
  handler    = "extract_data.lambda_handler"
  depends_on = [aws_cloudwatch_log_group.ingest_function_log_group]

  runtime       = "python3.14"
  architectures = ["x86_64"]

  timeout     = 30
  memory_size = 1024

  source_code_hash = data.archive_file.ingest_function.output_base64sha256

  layers = [
    aws_lambda_layer_version.lambda_layer.arn,
    "arn:aws:lambda:eu-west-2:336392948345:layer:AWSSDKPandas-Python314:11"
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
  compatible_runtimes = ["python3.14"]
}

data "archive_file" "lambda_layer" {
  type        = "zip"
  source_dir  = "${path.module}/../lambda_layers/ingest/build"
  output_path = "${path.module}/lambda_layer.zip"
}

resource "aws_lambda_function" "transform_data" {
  function_name = "transform-data"

  s3_bucket = aws_s3_bucket.code.bucket
  s3_key    = aws_s3_object.transform_function_zip.key

  role = aws_iam_role.transform_lambda_role.arn

  handler = "lambda_handler_placeholder.lambda_handler"

  runtime       = "python3.14"
  architectures = ["x86_64"]

  timeout     = 30
  memory_size = 1024

  source_code_hash = data.archive_file.transform_function.output_base64sha256

  layers = [
    aws_lambda_layer_version.transform_s3fs_layer.arn,
    "arn:aws:lambda:eu-west-2:336392948345:layer:AWSSDKPandas-Python314:11"
  ]
  environment {
    variables = {
      INGEST_BUCKET    = aws_s3_bucket.ingestion_zone.id
      PROCESSED_BUCKET = aws_s3_bucket.processed_zone.id
    }
  }
}

resource "aws_s3_object" "transform_function_zip" {
  bucket = aws_s3_bucket.code.id
  key    = "transform/transform_function.zip"

  source      = data.archive_file.transform_function.output_path
  source_hash = data.archive_file.transform_function.output_base64sha256
}

data "archive_file" "transform_function" {
  type        = "zip"
  source_file = "${path.module}/../transform/lambda_handler_placeholder.py"
  output_path = "${path.module}/transform_function.zip"
}

resource "aws_lambda_layer_version" "transform_s3fs_layer" {
  s3_bucket = aws_s3_bucket.code.id
  s3_key    = aws_s3_object.transform_layer_zip.key

  source_code_hash = data.archive_file.transform_layer.output_base64sha256

  layer_name          = "transform_s3fs_layer"
  compatible_runtimes = ["python3.14"]
}

resource "aws_s3_object" "transform_layer_zip" {
  bucket = aws_s3_bucket.code.id
  key    = "layers/transform_s3fs_layer.zip"

  source      = data.archive_file.transform_layer.output_path
  source_hash = data.archive_file.transform_layer.output_base64sha256
}

data "archive_file" "transform_layer" {
  type        = "zip"
  source_dir  = "${path.module}/../lambda_layers/transform/build"
  output_path = "${path.module}/transform_layer.zip"
}