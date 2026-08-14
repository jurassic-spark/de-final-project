# Trust policy shared by both Lambda execution roles.
# This allows the AWS Lambda service to assume these roles when functions run.
data "aws_iam_policy_document" "lambda_assume_role" {
  statement {
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

# Runtime role for the extract Lambda.
# Permissions are attached separately below.
resource "aws_iam_role" "extract_lambda_role" {
  name_prefix        = "role-extract-lambda-"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
}

# Runtime role for the transform Lambda.
resource "aws_iam_role" "transform_lambda_role" {
  name_prefix        = "role-transform-lambda-"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
}

# Looks up the existing Totesys credentials secret.
data "aws_secretsmanager_secret" "totesys_credentials" {
  name = "totesys_database_credentials"
}

# Grants the Lambda permission to write objects
# only to the ingestion S3 bucket.
resource "aws_iam_policy" "extract_s3_policy" {
  name = "extract-lambda-s3-access"

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Sid      = "WriteRawData"
        Effect   = "Allow"
        Action   = ["s3:PutObject"]
        Resource = "${aws_s3_bucket.ingestion_zone.arn}/*"
      },
      {
        Sid      = "ListIngestionBucket"
        Effect   = "Allow"
        Action   = ["s3:ListBucket"]
        Resource = aws_s3_bucket.ingestion_zone.arn
      }
    ]
  })
}

# Grants the Lambda permission to retrieve the Totesys database credentials
# from AWS Secrets Manager. Access is restricted to the specific secret
# referenced above.
resource "aws_iam_policy" "extract_secrets_policy" {
  name = "extract-lambda-secrets-access"

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Sid      = "ReadTotesysCredentials"
        Effect   = "Allow"
        Action   = ["secretsmanager:GetSecretValue"]
        Resource = data.aws_secretsmanager_secret.totesys_credentials.arn
      }
    ]
  })
}

# Grants the Lambda function permission to create CloudWatch log groups and streams
# and write log events to CloudWatch Logs.
resource "aws_iam_policy" "lambda_function_logging_policy" {
  name   = "function-logging-policy"
  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        Action : [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        Effect : "Allow",
        Resource : "arn:aws:logs:*:*:*"
      }
    ]
  })
}

# Grants the Lambda permission to retrieve objects from raw s3 ingestion_zone
# and write transformed objects to the processed zone.
resource "aws_iam_policy" "transform_s3_policy" {
  name = "transform-lambda-s3-access"

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Sid      = "ReadRawData"
        Effect   = "Allow"
        Action   = ["s3:GetObject"]
        Resource = "${aws_s3_bucket.ingestion_zone.arn}/*"
      },
      {
        Sid      = "WriteProcessedData"
        Effect   = "Allow"
        Action   = ["s3:PutObject"]
        Resource = "${aws_s3_bucket.processed_zone.arn}/*"
      }
    ]
  })
}

# Give the extract Lambda permission to write raw data to S3.
resource "aws_iam_role_policy_attachment" "extract_s3_attach" {
  role       = aws_iam_role.extract_lambda_role.name
  policy_arn = aws_iam_policy.extract_s3_policy.arn
}

# Attaches the CloudWatch logging policy to the Lambda execution role,
# allowing the function to write logs to CloudWatch Logs.
resource "aws_iam_role_policy_attachment" "function_logging_policy_attach" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_function_logging_policy.arn
}

# Give the extract Lambda permission to retrieve database credentials.
resource "aws_iam_role_policy_attachment" "extract_secrets_attach" {
  role       = aws_iam_role.extract_lambda_role.name
  policy_arn = aws_iam_policy.extract_secrets_policy.arn
}

resource "aws_iam_role_policy_attachment" "extract_logging_attach" {
  role       = aws_iam_role.extract_lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Give the transform Lambda permission to read raw data and write processed data.
resource "aws_iam_role_policy_attachment" "transform_s3_attach" {
  role       = aws_iam_role.transform_lambda_role.name
  policy_arn = aws_iam_policy.transform_s3_policy.arn
}