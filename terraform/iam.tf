# IAM execution role assumed by the Lambda function at runtime.
# Permissions required by the Lambda are attached to this role separately.
resource "aws_iam_role" "lambda_role" {
  name_prefix        = "role-${var.lambda_name}"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
}

# Defines the trust policy for the Lambda execution role.
# Allows the AWS Lambda service to assume the role.
data "aws_iam_policy_document" "lambda_assume_role" {
  statement {

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

# Retrieves metadata for the existing Totesys database credentials secret.
# The secret ARN is used to restrict the Lambda's Secrets Manager permissions
# to this specific secret.
data "aws_secretsmanager_secret" "totesys_credentials" {
  name = "totesys_database_credentials"
}

# Grants the Lambda permission to write objects to S3.
# This will be scoped to the target ingestion bucket once that bucket
# is provisioned.
resource "aws_iam_policy" "lambda_put_policy" {
  name = "lambda_put_policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid      = "Statement1"
        Effect   = "Allow"
        Action   = ["s3:PutObject"]
        Resource = "*"
      }
    ]
  })
}

# Grants the Lambda permission to retrieve the Totesys database credentials
# from AWS Secrets Manager. Access is restricted to the specific secret
# referenced above.
resource "aws_iam_policy" "lambda_secrets_policy" {
  name = "lambda-secrets-access"

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
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


# Attaches the S3 write policy to the Lambda execution role,
# allowing the function to save extracted data to S3.
resource "aws_iam_role_policy_attachment" "lambda_s3_attach" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_put_policy.arn
}

# Attaches the Secrets Manager policy to the Lambda execution role,
# allowing the function to retrieve the database credentials at runtime.
resource "aws_iam_role_policy_attachment" "lambda_secrets_attach" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_secrets_policy.arn
}

# Attaches the CloudWatch logging policy to the Lambda execution role,
# allowing the function to write logs to CloudWatch Logs.
resource "aws_iam_role_policy_attachment" "function_logging_policy_attach" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_function_logging_policy.arn
}