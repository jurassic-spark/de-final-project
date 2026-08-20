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

resource "aws_security_group" "warehouse_rds" {
  name        = "jurassic-sparks-warehouse-rds-sg"
  description = "Allow PostgreSQL access from the load Lambda"
  vpc_id      = data.aws_vpc.default.id

  # Permanent application access.
  ingress {
    description = "PostgreSQL from load Lambda"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"

    security_groups = [
      aws_security_group.load_lambda.id,
      aws_security_group.schema_load_lambda.id
    ]
  }

  # Temporary access from zero, one or multiple exact public IPs.
  dynamic "ingress" {
    for_each = var.temporary_warehouse_admin_cidrs
    iterator = administrator_cidr

    content {
      description = "TEMPORARY PostgreSQL access from administrator"
      from_port   = 5432
      to_port     = 5432
      protocol    = "tcp"
      cidr_blocks = [administrator_cidr.value]
    }
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

# Security Group for the VPC Endpoint
resource "aws_security_group" "vpc_endpoint_sg" {
  name        = "secretsmanager-vpc-endpoint-sg"
  description = "Security group for Secrets Manager VPC Interface Endpoint"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description     = "Allow HTTPS ingress from Lambda functions"
    from_port       = 443
    to_port         = 443
    protocol        = "tcp"
    security_groups = [aws_security_group.schema_load_lambda.id]
  }
}

# 3. Secrets Manager Interface VPC Endpoint
resource "aws_vpc_endpoint" "secretsmanager" {
  vpc_id            = data.aws_vpc.default.id
  service_name      = "com.amazonaws.eu-west-2.secretsmanager"
  vpc_endpoint_type = "Interface"

  subnet_ids = [
    sort(data.aws_subnets.default.ids)[0]
  ]

  security_group_ids = [
    aws_security_group.vpc_endpoint_sg.id
  ]

  private_dns_enabled = true
}