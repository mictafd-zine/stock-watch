output "lambda_function_name" {
  description = "Name of the Lambda function"
  value       = aws_lambda_function.data_ingestion_lambda.function_name
}

output "cloudwatch_rule_name" {
  description = "CloudWatch rule for scheduling"
  value       = aws_cloudwatch_event_rule.every_hour.name
}

output "s3_bucket_name" {
  description = "S3 bucket name for data storage"
  value       = aws_s3_bucket.raw_data_storage_bucket.bucket
}
