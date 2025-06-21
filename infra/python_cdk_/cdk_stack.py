from aws_cdk import Stack, Duration
from constructs import Construct
from aws_cdk import (
    aws_lambda as _lambda,
    aws_ecr as ecr,
    aws_iam as iam,
    aws_s3 as s3,
    aws_secretsmanager as secretsmanager,
    aws_events as events,
    aws_events_targets as targets,
)

class InfraStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # Import existing secret
        secret = secretsmanager.Secret.from_secret_name_v2(
            self, "AlphaVantageSecret", secret_name="AlphaVantageAPIKeyv1"
        )

        # Import existing ECR repository
        repository = ecr.Repository.from_repository_name(
            self, "LambdaEcrRepo", repository_name="stock-watch-repo"
        )

        # Import existing S3 bucket
        bucket = s3.Bucket.from_bucket_name(
            self, "DataLandingBucket", bucket_name="alpha-vantage-data-storage"
        )

        # Import existing IAM role
        lambda_role = iam.Role.from_role_name(
            self, "ImportedLambdaRole",
            role_name="AlphaVantageLambdaDataIngestion_role"
        )

        # Import existing Lambda function by name
        lambda_fn = _lambda.DockerImageFunction(
            self, "AlphaVantageLambdaFunction",
            function_name="AlphaVantageLambdaDataIngestion",
            code=_lambda.DockerImageCode.from_ecr(repository),
            role=lambda_role,memory_size=1024,  # in MB
            timeout=Duration.minutes(15),
            environment={
                "SECRET_NAME": secret.secret_name,
                "REGION": "eu-west-1"
            }
            )


        rule = events.Rule(
            self, "Every5MinRule",
            schedule=events.Schedule.rate(Duration.minutes(5))
        )
        rule.add_target(targets.LambdaFunction(lambda_fn))

