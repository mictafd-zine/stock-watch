#!/usr/bin/env python3
import aws_cdk as cdk
from python_cdk_.cdk_stack import InfraStack

app = cdk.App()

InfraStack(app, "InfraStack")

app.synth() 
