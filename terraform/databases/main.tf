# --- 1. Security Group for Databases ---
resource "aws_security_group" "db_sg" {
  name        = "openedx-data-sg"
  description = "Allow DB traffic from VPC"
  vpc_id      = var.vpc_id # Variable se ayega

  # MySQL
  ingress {
    from_port   = 3306
    to_port     = 3306
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"]
  }
  # MongoDB
  ingress {
    from_port   = 27017
    to_port     = 27017
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"]
  }
  # Redis
  ingress {
    from_port   = 6379
    to_port     = 6379
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"]
  }
  # Elasticsearch
  ingress {
    from_port   = 9200
    to_port     = 9200
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Name = "openedx-data-sg" }
}

# --- 2. RDS Subnet Group ---
resource "aws_db_subnet_group" "default" {
  name       = "openedx-db-subnet-group"
  subnet_ids = [var.private_data_subnet_1_id, var.private_data_subnet_2_id]

  tags = { Name = "OpenEdX DB Subnet Group" }
}

# --- 3. MySQL RDS Instance ---
resource "aws_db_instance" "mysql" {
  allocated_storage      = 20
  db_name                = "openedx"
  engine                 = "mysql"
  engine_version         = "8.0"
  instance_class         = "db.t3.micro"
  username               = "admin"
  password               = "OpenEdXStrongPass123!" # Production me Secrets Manager use hota hai
  parameter_group_name   = "default.mysql8.0"
  skip_final_snapshot    = true
  db_subnet_group_name   = aws_db_subnet_group.default.name
  vpc_security_group_ids = [aws_security_group.db_sg.id]

  tags = { Name = "openedx-mysql" }
}
