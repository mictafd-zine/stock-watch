# Fetch the secret using its name from Secrets Manager
data "aws_secretsmanager_secret" "alpha_vantage_secret" {
  name = var.alpha_vantage_secret_name
}

data "aws_ecr_repository" "lambda_repository" {
  name = var.ecr_repository_name  # The name of the existing repository
}

resource "aws_iam_role" "data_ingestion_lambda_role" {
  name = "${var.lambda_function_name}_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}


# IAM Policy that uses the secret ARN dynamically
resource "aws_iam_policy" "data_ingestion_lambda_policy" {
  name        = "${var.lambda_function_name}_policy"
  description = "Policy for Lambda to access Secrets Manager and S3 (optional)"
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Effect   = "Allow"
        Resource = data.aws_secretsmanager_secret.alpha_vantage_secret.arn  # Dynamically resolve ARN
      },
      {
        Action   = ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"],
        Effect   = "Allow",
        Resource = "*"
      },
      # Combined Permissions for S3 (PutObject, GetObject, ListBucket)
      {
        Action   = [
          "s3:PutObject",
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Effect   = "Allow"
        Resource = [
          "arn:aws:s3:::${var.s3_bucket_name}/*", # Allows PutObject and GetObject on all objects in the bucket
          "arn:aws:s3:::${var.s3_bucket_name}"    # Allows ListBucket on the bucket itself
        ]
      }
    ]
  })
}

# Lambda function definition
resource "aws_lambda_function" "data_ingestion_lambda" {
  function_name = var.lambda_function_name
  role          = aws_iam_role.data_ingestion_lambda_role.arn
  package_type  = "Image"  # Specify that the deployment is container-based

  # Reference the Docker image URI from the ECR repository
  image_uri = "${data.aws_ecr_repository.lambda_repository.repository_url}:${var.docker_image_tag}"

  environment {
    variables = {
      SECRET_NAME = var.alpha_vantage_secret_name  # Keep the secret name in environment variables
      REGION      = var.aws_region
      S3_BUCKET   = var.s3_bucket_name
    }
  }

  timeout     = 10
  memory_size = 128
}

# CloudWatch event and other resources as previously defined
resource "aws_cloudwatch_event_rule" "every_hour" {
  name                = "EveryHour"
  schedule_expression = "rate(1 hour)"
}

resource "aws_cloudwatch_event_target" "lambda_target" {
  rule      = aws_cloudwatch_event_rule.every_hour.name
  target_id = var.lambda_function_name
  arn       = aws_lambda_function.data_ingestion_lambda.arn
}

resource "aws_lambda_permission" "allow_cloudwatch" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.data_ingestion_lambda.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.every_hour.arn
}

resource "aws_s3_bucket" "raw_data_storage_bucket" {
  bucket = var.s3_bucket_name
}

resource "aws_iam_role_policy_attachment" "data_ingestion_lambda_policy_attachment" {
  role       = aws_iam_role.data_ingestion_lambda_role.name
  policy_arn = aws_iam_policy.data_ingestion_lambda_policy.arn
}
