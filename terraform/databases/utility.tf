# --- 4. Utility EC2 Instance (Mongo, Redis, Elastic) ---
resource "aws_instance" "utility_server" {
  ami                    = "ami-0c7217cdde317cfec" # Ubuntu 22.04 LTS (us-east-1)
  instance_type          = "t3.medium"             # Production standard (t2.medium bhi chalega)
  key_name               = "adeel-key"             # Apna Key name confirm karein
  subnet_id              = var.private_data_subnet_1_id # Variable se subnet ID ayegi
  vpc_security_group_ids = [aws_security_group.utility_sg.id]

  # Private IP ensure karne ke liye (Optional but good for stability)
  private_ip = "10.0.5.90"

  tags = {
    Name        = "openedx-data-utility"
    Environment = "Production"
    Role        = "Database-Host"
  }
}

# --- 5. Security Group for Utility Server ---
resource "aws_security_group" "utility_sg" {
  name        = "openedx-utility-sg"
  description = "Allow DB ports from VPC only"
  vpc_id      = var.vpc_id

  # SSH Internal Access
  ingress {
    from_port   = 22
    to_port     = 22
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
}
