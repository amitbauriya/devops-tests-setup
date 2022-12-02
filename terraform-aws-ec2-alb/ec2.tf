##########################################################################################

# Creating 3 EC2 Instances

##########################################################################################

resource "aws_instance" "instance" {
  count                = length(aws_subnet.aws_subnet_ids.subnet.id
  ami                  = var.ami_id
  instance_type        = var.instance_type
  subnet_id            = element(aws_subnet.aws_subnet_ids.subnet.id, count.index)
  security_groups      = [aws_security_group.sg.id, ]
  key_name             = "amit"
  iam_instance_profile = data.aws_iam_role.iam_role.name
	user_data = <<-EOF
	      #!/bin/bash
		    sudo yum update -y
		    sudo yum -y install httpd -y
		    sudo service httpd start
		    echo "Accrete - Instance $(hostname -f)" > /var/www/html/index.html
		    EOF

  tags = {
    "Name"        = "accrete-test-${count.index}"
    "Environment" = "Test"
    "CreatedBy"   = "Terraform"
  }

  timeouts {
    create = "10m"
  }

}

############################################################################################

# Creating 3 Elastic IPs (Optional)

############################################################################################

resource "aws_eip" "eip" {
  count            = length(aws_instance.instance.*.id)
  instance         = element(aws_instance.instance.*.id, count.index)
  public_ipv4_pool = "amazon"
  vpc              = true

  tags = {
    "Name" = "EIP-${count.index}"
  }
}

############################################################################################

# Creating EIP association with EC2 Instances  (Optional)

############################################################################################

resource "aws_eip_association" "eip_association" {
  count         = length(aws_eip.eip)
  instance_id   = element(aws_instance.instance.*.id, count.index)
  allocation_id = element(aws_eip.eip.*.id, count.index)
}
