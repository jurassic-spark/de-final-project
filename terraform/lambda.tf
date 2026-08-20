resource "aws_s3_object" "ingest_function_zip" {
  bucket = aws_s3_bucket.code.id
  key    = "ingest_raw_data/ingest_function.zip"

  source      = data.archive_file.ingest_function.output_path
  source_hash = data.archive_file.ingest_function.output_base64sha256
}

# Upload the ingest Lambda layer zip to the code bucket.
resource "aws_s3_object" "ingest_lambda_layer_zip" {
  bucket = aws_s3_bucket.code.id
  key    = "layers/ingest_function_layer.zip"

  source      = data.archive_file.ingest_lambda_layer.output_path
  source_hash = data.archive_file.ingest_lambda_layer.output_base64sha256
}

# Upload the transform Lambda layer zip to the code bucket.
resource "aws_s3_object" "transform_layer_zip" {
  bucket = aws_s3_bucket.code.id
  key    = "layers/transform_function_layer.zip"

  source      = data.archive_file.transform_layer.output_path
  source_hash = data.archive_file.transform_layer.output_base64sha256
}

resource "aws_lambda_function" "ingest_raw_data" {
  function_name = var.ingest_lambda_name
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
    aws_lambda_layer_version.ingest_lambda_layer.arn,
    "arn:aws:lambda:eu-west-2:336392948345:layer:AWSSDKPandas-Python313:9"
  ]

  environment {
    variables = {
      INGEST_BUCKET = aws_s3_bucket.ingestion_zone.id
    }
  }

  logging_config {
    log_format = "Text"
    log_group  = aws_cloudwatch_log_group.ingest_function_log_group.name
  }
}

# Package the ingest Lambda function code.
data "archive_file" "ingest_function" {
  type        = "zip"
  source_file = "${path.module}/../ingestion/extract_data.py"
  output_path = "${path.module}/ingest_lambda_layer_zip"
}

# Provision the custom ingest dependency layer.
resource "aws_lambda_layer_version" "ingest_lambda_layer" {
  s3_bucket = aws_s3_bucket.code.id
  s3_key    = aws_s3_object.ingest_lambda_layer_zip.key

  source_code_hash = data.archive_file.ingest_lambda_layer.output_base64sha256

  layer_name          = "ingest_function_layer"
  compatible_runtimes = ["python3.13"]

  lifecycle {
    create_before_destroy = true
  }
}

# Package the custom ingest dependencies.
data "archive_file" "ingest_lambda_layer" {
  type        = "zip"
  source_dir  = "${path.module}/../lambda_layers/ingest/build"
  output_path = "${path.module}/lambda_layer.zip"
}

# Provision the custom transform dependency layer.
resource "aws_lambda_layer_version" "transform_layer" {
  s3_bucket = aws_s3_bucket.code.id
  s3_key    = aws_s3_object.transform_layer_zip.key

  source_code_hash = data.archive_file.transform_layer.output_base64sha256

  layer_name          = "transform_function_layer"
  compatible_runtimes = ["python3.13"]

  lifecycle {
    create_before_destroy = true
  }
}

# Package the custom transform dependencies.
data "archive_file" "transform_layer" {
  type        = "zip"
  source_dir  = "${path.module}/../lambda_layers/transform/build"
  output_path = "${path.module}/transform_layer.zip"
}

resource "aws_lambda_function" "schema_load_lambda" {
  function_name = var.schema_load_lambda_name
  s3_bucket     = aws_s3_bucket.code.bucket
  s3_key        = aws_s3_object.schema_load_function_zip.key

  role          = aws_iam_role.schema_load_lambda_role.arn
  handler       = "schema_load.lambda_handler"
  runtime       = "python3.13"
  architectures = ["x86_64"]

  timeout     = 900
  memory_size = 1024

  source_code_hash = data.archive_file.load_schema_function.output_base64sha256

  layers = [
    aws_lambda_layer_version.ingest_lambda_layer.arn,
    "arn:aws:lambda:eu-west-2:336392948345:layer:AWSSDKPandas-Python313:9"
  ]

  vpc_config {
    subnet_ids = data.aws_subnets.default.ids

    security_group_ids = [
      aws_security_group.schema_load_lambda.id
    ]
  }

  environment {
    variables = {
      WAREHOUSE_SECRET_NAME = aws_db_instance.warehouse.master_user_secret[0].secret_arn
      WAREHOUSE_NAME        = aws_db_instance.warehouse.db_name
      HOST                  = aws_db_instance.warehouse.address
      PORT                  = tostring(aws_db_instance.warehouse.port)
      USER                  = aws_db_instance.warehouse.username
    }
  }
  #Ensures policy attachment takes place before network connection
  depends_on = [
    aws_iam_role_policy_attachment.schema_load_lambda_vpc_attach
  ]
}

resource "aws_s3_object" "schema_load_function_zip" {
  bucket = aws_s3_bucket.code.id
  key    = "load_schema/schema_load_function_zip"

  source      = data.archive_file.load_schema_function.output_path
  source_hash = data.archive_file.load_schema_function.output_base64sha256
}

data "archive_file" "load_schema_function" {
  type        = "zip"
  source_file = "${path.module}/../schema/schema_load.py"
  output_path = "${path.module}/schema_load_function_zip"
}