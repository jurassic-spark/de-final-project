variable "ingest_lambda_name" {
  type    = string
  default = "ingest_raw_data"
}

variable "notification_emails" {
  type = set(string)
}

variable "warehouse_db_name" {
  description = "Name of the warehouse PostgreSQL database"
  type        = string
  default     = "jurassic_sparks_warehouse"
}

variable "warehouse_master_username" {
  description = "Master username for the warehouse database"
  type        = string
  default     = "postgres"
}

variable "schema_load_lambda_name" {
  type    = string
  default = "schema_load_lambda"
}