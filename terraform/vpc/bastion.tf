# --- Bastion Host Security Group ---
resource "aws_security_group" "bastion_sg" {
  name        = "openedx-bastion-sg"
  description = "Allow SSH from Admin IP"
  vpc_id      = aws_vpc.main.id  # Ya var.vpc_id agar module use kar rahe hain

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # Best Practice: Yahan apni real IP variable se pass karein
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Name = "openedx-bastion-sg" }
}

# --- Bastion EC2 Instance ---
resource "aws_instance" "bastion" {
  ami                         = "ami-0c7217cdde317cfec" # Ubuntu 22.04 LTS
  instance_type               = "t2.micro"
  key_name                    = "adeel-key"
  subnet_id                   = aws_subnet.public_1.id # Must be Public
  vpc_security_group_ids      = [aws_security_group.bastion_sg.id]
  associate_public_ip_address = true # Important

  tags = {
    Name = "openedx-bastion"
    Role = "Jump-Server"
  }
}
