terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

resource "aws_s3_bucket" "catalogue_exports" {
  bucket = "${var.app_name}-${var.environment}-exports"

  tags = {
    Name        = "catalogue-exports"
    Environment = var.environment
    Application = var.app_name
  }
}

resource "aws_s3_bucket_versioning" "catalogue_exports" {
  bucket = aws_s3_bucket.catalogue_exports.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "catalogue_exports_retention" {
  bucket = aws_s3_bucket.catalogue_exports.id

  rule {
    id     = "retain-90-days"
    status = "Enabled"

    expiration {
      days = 90
    }
  }
}

resource "aws_iam_role" "catalogue_sync_worker" {
  name = "${var.app_name}-${var.environment}-worker"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}

data "aws_iam_policy_document" "catalogue_sync_s3" {
  statement {
    effect = "Allow"
    actions = [
      "s3:GetObject",
      "s3:PutObject",
      "s3:ListBucket"
    ]
    resources = [
      aws_s3_bucket.catalogue_exports.arn,
      "${aws_s3_bucket.catalogue_exports.arn}/*"
    ]
  }
}

resource "aws_iam_policy" "catalogue_sync_s3" {
  name   = "${var.app_name}-${var.environment}-s3-access"
  policy = data.aws_iam_policy_document.catalogue_sync_s3.json
}

resource "aws_iam_role_policy_attachment" "catalogue_sync_s3" {
  role       = aws_iam_role.catalogue_sync_worker.name
  policy_arn = aws_iam_policy.catalogue_sync_s3.arn
}

resource "aws_cloudwatch_log_group" "catalogue_sync" {
  name              = "/aws/catalogue-sync/${var.environment}"
  retention_in_days = 30
}
