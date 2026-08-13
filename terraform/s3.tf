# Retrieves the AWS account ID to help create globally unique bucket names.
data "aws_caller_identity" "current" {}

# Stores code for the data pipeline.
resource "aws_s3_bucket" "code" {
  bucket        = "js-final-proj-code-${data.aws_caller_identity.current.account_id}-dev"
  force_destroy = true

  tags = {
    Name        = "Code Bucket"
    Environment = "Dev"
  }
}

# Versioning enabled to help with recovery and support rollback
resource "aws_s3_bucket_versioning" "code" {
  bucket = aws_s3_bucket.code.id

  versioning_configuration {
    status = "Enabled"
  }
}

# Stores raw data extracted from the Totesys source database.
resource "aws_s3_bucket" "ingestion_zone" {
  bucket = "js-final-proj-ingested-${data.aws_caller_identity.current.account_id}-dev"

  tags = {
    Name        = "Ingest Raw Data Bucket"
    Environment = "Dev"
  }
}

# Versioning enabled to help with recovery
resource "aws_s3_bucket_versioning" "ingestion_zone" {
  bucket = aws_s3_bucket.ingestion_zone.id

  versioning_configuration {
    status = "Enabled"
  }
}

# Stores transform data
resource "aws_s3_bucket" "processed_zone" {
  bucket = "js-final-proj-processed-${data.aws_caller_identity.current.account_id}-dev"

  tags = {
    Name        = "Processed Data Bucket"
    Environment = "Dev"
  }
}

# Versioning enabled to help with recovery
resource "aws_s3_bucket_versioning" "processed_zone" {
  bucket = aws_s3_bucket.processed_zone.id

  versioning_configuration {
    status = "Enabled"
  }
}

#Public access blocks for s3 storage
#https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket_public_access_block
resource "aws_s3_bucket_public_access_block" "code_bucket" {
  bucket = aws_s3_bucket.code.id

  block_public_acls       = true
  ignore_public_acls      = true
  block_public_policy     = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_public_access_block" "ingestion_zone" {
  bucket = aws_s3_bucket.ingestion_zone.id

  block_public_acls       = true
  ignore_public_acls      = true
  block_public_policy     = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_public_access_block" "processed_zone" {
  bucket = aws_s3_bucket.processed_zone.id

  block_public_acls       = true
  ignore_public_acls      = true
  block_public_policy     = true
  restrict_public_buckets = true
}