provider "aws" {
  region = "us-east-1"
}

# --- 1. VPC ---
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags = { Name = "openedx-vpc" }
}

# --- 2. Internet Gateway ---
resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main.id
  tags   = { Name = "openedx-igw" }
}

# --- 3. Subnets (6 Total) ---

# Public Subnets (Load Balancer / NAT)
resource "aws_subnet" "public_1" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "us-east-1a"
  map_public_ip_on_launch = true
  tags                    = { Name = "public-subnet-1" }
}

resource "aws_subnet" "public_2" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.2.0/24"
  availability_zone       = "us-east-1b"
  map_public_ip_on_launch = true
  tags                    = { Name = "public-subnet-2" }
}

# Private App Subnets (EKS Nodes)
resource "aws_subnet" "private_app_1" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.3.0/24"
  availability_zone = "us-east-1a"
  tags              = { Name = "private-app-subnet-1" }
}

resource "aws_subnet" "private_app_2" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.4.0/24"
  availability_zone = "us-east-1b"
  tags              = { Name = "private-app-subnet-2" }
}

# Private Data Subnets (Databases - Isolated)
resource "aws_subnet" "private_data_1" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.5.0/24"
  availability_zone = "us-east-1a"
  tags              = { Name = "private-data-subnet-1" }
}

resource "aws_subnet" "private_data_2" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.6.0/24"
  availability_zone = "us-east-1b"
  tags              = { Name = "private-data-subnet-2" }
}

# --- 4. NAT Gateway Configuration ---
resource "aws_eip" "nat" {
  domain = "vpc"
}

resource "aws_nat_gateway" "nat" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.public_1.id # Must be in Public Subnet
  tags          = { Name = "openedx-nat" }
}

# --- 5. Route Tables ---

# Public Route Table
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }
  tags = { Name = "openedx-public-rt" }
}

# Private App Route Table (Through NAT)
resource "aws_route_table" "private_app" {
  vpc_id = aws_vpc.main.id
  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.nat.id
  }
  tags = { Name = "openedx-private-app-rt" }
}

# Private Data Route Table (Local Only - No Internet)
resource "aws_route_table" "private_data" {
  vpc_id = aws_vpc.main.id
  # No route to 0.0.0.0/0 ensures isolation
  tags   = { Name = "openedx-private-data-rt" }
}

# --- 6. Route Table Associations ---

# Public Associations
resource "aws_route_table_association" "pub_1" {
  subnet_id      = aws_subnet.public_1.id
  route_table_id = aws_route_table.public.id
}
resource "aws_route_table_association" "pub_2" {
  subnet_id      = aws_subnet.public_2.id
  route_table_id = aws_route_table.public.id
}

# Private App Associations
resource "aws_route_table_association" "app_1" {
  subnet_id      = aws_subnet.private_app_1.id
  route_table_id = aws_route_table.private_app.id
}
resource "aws_route_table_association" "app_2" {
  subnet_id      = aws_subnet.private_app_2.id
  route_table_id = aws_route_table.private_app.id
}

# Private Data Associations
resource "aws_route_table_association" "data_1" {
  subnet_id      = aws_subnet.private_data_1.id
  route_table_id = aws_route_table.private_data.id
}
resource "aws_route_table_association" "data_2" {
  subnet_id      = aws_subnet.private_data_2.id
  route_table_id = aws_route_table.private_data.id
}

