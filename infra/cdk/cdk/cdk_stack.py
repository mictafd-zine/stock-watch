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

        # Imported resources
        secret = secretsmanager.Secret.from_secret_name_v2(
            self, "AlphaVantageSecret", secret_name="your-secret-name"
        )

        repository = ecr.Repository.from_repository_name(
            self, "LambdaEcrRepo", repository_name="your-repo-name"
        )

        bucket = s3.Bucket.from_bucket_name(
            self, "DataStorageBucket", bucket_name="your-bucket-name"
        )

        # IAM Role
        lambda_role = iam.Role(
            self, "LambdaRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            role_name="your-lambda-role-name"
        )

        # IAM Policy
        policy = iam.Policy(
            self, "LambdaPolicy",
            statements=[
                iam.PolicyStatement(
                    actions=["secretsmanager:GetSecretValue"],
                    resources=[secret.secret_arn]
                ),
                iam.PolicyStatement(
                    actions=["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"],
                    resources=["*"]
                ),
                iam.PolicyStatement(
                    actions=["s3:PutObject", "s3:GetObject", "s3:ListBucket"],
                    resources=[
                        f"arn:aws:s3:::{bucket.bucket_name}",
                        f"arn:aws:s3:::{bucket.bucket_name}/*"
                    ]
                )
            ]
        )
        policy.attach_to_role(lambda_role)

        # Lambda function (from ECR image)
        lambda_fn = _lambda.DockerImageFunction(
            self, "DataIngestionLambda",
            function_name="your-lambda-name",
            role=lambda_role,
            code=_lambda.DockerImageCode.from_ecr(repository, tag="your-tag"),
            environment={
                "SECRET_NAME": "your-secret-name",
                "REGION": "your-region",
                "S3_BUCKET": bucket.bucket_name
            },
            timeout=Duration.seconds(10),
            memory_size=128
        )

        # CloudWatch event rule and target
        rule = events.Rule(
            self, "HourlyTrigger",
            schedule=events.Schedule.rate(Duration.hours(1))
        )
        rule.add_target(targets.LambdaFunction(lambda_fn))

        # Lambda permission for CloudWatch
        _lambda.CfnPermission(
            self, "AllowCloudWatchInvoke",
            action="lambda:InvokeFunction",
            function_name=lambda_fn.function_name,
            principal="events.amazonaws.com",
            source_arn=rule.rule_arn
        )
