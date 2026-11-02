provider "aws" {
  region = var.aws_region
}

variable "aws_region" {
  type        = string
  description = "AWS region for future EKS deployment"
  default     = "ap-south-1"
}

output "deployment_status" {
  value = "Scaffold only; add reviewed VPC/EKS modules before provisioning."
}
