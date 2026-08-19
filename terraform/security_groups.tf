data "aws_vpc" "default" {
  default = true
}

# Security group for the Lambda responsible for loading
# transformed data into the RDS warehouse.
resource "aws_security_group" "load_lambda" {
  name        = "jurassic-sparks-load-lambda-sg"
  description = "Security group for warehouse load Lambda"
  vpc_id      = data.aws_vpc.default.id

  egress {
    description = "Allow outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "jurassic-sparks-load-lambda-sg"
  }
}

# Security group for the PostgreSQL warehouse.
resource "aws_security_group" "warehouse_rds" {
  name        = "jurassic-sparks-warehouse-rds-sg"
  description = "Allow PostgreSQL access from the load Lambda"
  vpc_id      = data.aws_vpc.default.id

  # Only resources using the load Lambda security group
  # can initiate PostgreSQL connections to the warehouse.
  ingress {
    description     = "PostgreSQL from load Lambda"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.load_lambda.id, aws_security_group.schema_load_lambda.id]
  }

  tags = {
    Name = "jurassic-sparks-warehouse-rds-sg"
  }
}

resource "aws_security_group" "schema_load_lambda" {
  name        = "jurassic-sparks-schema-load-lambda-sg"
  description = "Security group for schema load Lambda"
  vpc_id      = data.aws_vpc.default.id

  egress {
    description = "Allow outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "jurassic-sparks-schema-load-lambda-sg"
  }
}