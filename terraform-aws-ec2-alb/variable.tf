# EC2 Intances

variable "instance_tenancy" {
  description = "it defines the tenancy of VPC. Whether it's dafault or dedicated"
  type        = string
  default     = "default"
}

variable "ami_id" {
  description = "ami id"
  type        = string
  default     = "ami-12345678"
}

variable "instance_type" {
  description = "Instance type to create an instance"
  type        = string
  default     = "t2.micro"
}

variable "ssh_private_key" {
  description = "pem file of Keypair we used to login to EC2 instances"
  type        = string
  default     = "./amit.pem"
}
