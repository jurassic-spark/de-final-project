resource "aws_scheduler_schedule" "thirty_min_pipeline_trigger" {
  name       = "thirty-min-pipeline-trigger"
  group_name = "default"
  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression = "cron(0/30 * * * ? *)"

  target {
    arn      = aws_sfn_state_machine.pipeline_sfn.arn
    role_arn = aws_iam_role.scheduler_assume_role.arn

    input = jsonencode(
      { trigger_source = "eventbridge_scheduler" }
    )
  }
}
