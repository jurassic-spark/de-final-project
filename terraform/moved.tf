# Record the new Terraform name for the existing ingest layer.
moved {
  from = aws_lambda_layer_version.lambda_layer
  to   = aws_lambda_layer_version.ingest_lambda_layer
}

# Record the new Terraform name for the existing layer package.
moved {
  from = aws_s3_object.lambda_layer_zip
  to   = aws_s3_object.ingest_lambda_layer_zip
}