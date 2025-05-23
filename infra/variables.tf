variable "aws_region" {
  description = "AWS region to deploy the resources"
  default     = "eu-west-1"
}

variable "lambda_function_name" {
  description = "The name of the Lambda function"
  default     = "AlphaVantageLambdaDataIngestion"
}

variable "s3_bucket_name" {
  description = "S3 bucket name for storing Alpha Vantage data"
  default     = "alpha-vantage-data-storage"
}

variable "alpha_vantage_secret_name" {
  description = "The name or ARN of the secret stored in AWS Secrets Manager"
  type        = string
}

variable "docker_image_name" {
  description = "Name of the Docker image for the Lambda function"
  default     = "stock-data-ingestion"
}

variable "docker_image_tag" {
  description = "Tag for the Docker image"
  default     = "latest"
}

variable "ecr_repository_name" {
  description = "Name of the ECR repository for storing the Docker image"
  default     = "stock-watch-repo"
}

