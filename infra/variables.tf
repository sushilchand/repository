variable "aws_region" {
  description = "AWS region for the catalogue sync infrastructure"
  type        = string
  default     = "ap-south-1"
}

variable "environment" {
  description = "Environment name for deployed infrastructure"
  type        = string
  default     = "dev"
}

variable "app_name" {
  description = "Application name used for AWS resource naming"
  type        = string
  default     = "catalogue-sync"
}
