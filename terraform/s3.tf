resource "aws_s3_bucket" "code" {
  bucket_prefix = "js-final-proj-code-"
  force_destroy = true

  tags = {
    Name        = "Code Bucket"
    Environment = "Dev"
  }
}