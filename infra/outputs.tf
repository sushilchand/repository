output "s3_bucket_name" {
  description = "Name of the raw export bucket"
  value       = aws_s3_bucket.catalogue_exports.bucket
}

output "log_group_name" {
  description = "CloudWatch log group for the catalogue sync worker"
  value       = aws_cloudwatch_log_group.catalogue_sync.name
}

output "worker_role_arn" {
  description = "IAM role ARN for the production sync worker"
  value       = aws_iam_role.catalogue_sync_worker.arn
}
