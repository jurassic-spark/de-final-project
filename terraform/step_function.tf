resource "aws_sfn_state_machine" "pipeline_sfn" {
  name     = "pipeline-sfn"
  role_arn = aws_iam_role.sfn_assume_role.arn
  definition = templatefile(
    "${path.module}/step_function_definition.json.tftpl",
    { ingest_lambda_arn = aws_lambda_function.ingest_raw_data.arn }
  )
}
