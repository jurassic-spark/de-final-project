variable "lambda_name" {
  type    = string
  default = "ingest_raw_data"
}

variable "notification_emails" {
  type      = set(string)
}