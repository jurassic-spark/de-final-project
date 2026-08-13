# Stores code for the data pipeline.
resource "aws_s3_bucket" "code" {
  bucket_prefix = "js-final-proj-code-"
  force_destroy = true

  tags = {
    Name        = "Code Bucket"
    Environment = "Dev"
  }
}

# Stores raw data extracted from the Totesys source database.
resource "aws_s3_bucket" "ingest" {
  bucket_prefix = "js-final-proj-ingest-"

  tags = {
    Name        = "Ingest Raw Data Bucket"
    Environment = "Dev"
  }
}

# Versioning enabled to help with recovery
resource "aws_s3_bucket_versioning" "ingest" {
  bucket = aws_s3_bucket.ingest.id

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

resource "aws_s3_bucket_public_access_block" "ingest" {
  bucket = aws_s3_bucket.ingest.id

  block_public_acls       = true
  ignore_public_acls      = true
  block_public_policy     = true
  restrict_public_buckets = true
}