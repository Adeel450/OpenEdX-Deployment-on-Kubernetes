# --- 1. Redis Security Group ---
resource "aws_security_group" "redis_sg" {
  name        = "openedx-redis-sg"
  description = "Allow Redis traffic"
  vpc_id      = var.vpc_id  # Ensure you have vpc_id variable defined

  ingress {
    from_port   = 6379
    to_port     = 6379
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr] # Allow access from within VPC
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "openedx-redis-sg"
  }
}

# --- 2. Redis Subnet Group (Private) ---
resource "aws_elasticache_subnet_group" "redis_subnet_group" {
  name       = "openedx-redis-subnet-group"
  subnet_ids = var.private_data_subnets # Must match your variable name
  description = "Redis Private Subnet Group"
}

# --- 3. Redis Replication Group (Cluster) ---
resource "aws_elasticache_replication_group" "redis" {
  replication_group_id       = "openedx-redis"
  description                = "OpenEdX Redis Cluster"
  node_type                  = "cache.t3.micro"
  port                       = 6379
  parameter_group_name       = "default.redis7"
  automatic_failover_enabled = true

  # Replicas Configuration (1 Primary + 1 Replica = 2 Nodes)
  num_cache_clusters         = 2
  multi_az_enabled           = true

  engine                     = "redis"
  engine_version             = "7.1"

  subnet_group_name          = aws_elasticache_subnet_group.redis_subnet_group.name
  security_group_ids         = [aws_security_group.redis_sg.id]

  tags = {
    Name = "openedx-redis"
  }
}

# --- 4. Output Endpoint ---
output "redis_primary_endpoint" {
  value = aws_elasticache_replication_group.redis.primary_endpoint_address
}
