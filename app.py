#!/usr/bin/env python3
import os
import json

import aws_cdk as cdk

from goldengate_cdk.goldengate_cdk_stack import GoldengateCdkStack


app = cdk.App()

# Use environment variables to keep the account information confidential
environment = cdk.Environment(
        account=os.environ.get("CDK_DEPLOYMENT_ACCOUNT", os.environ["CDK_DEFAULT_ACCOUNT"]),
        region=os.environ.get("CDK_DEPLOYMENT_REGION", os.environ["CDK_DEFAULT_REGION"]),
    )

# If you don't publish your source code and want to try it out with minimum overhaul,
# you can uncomment the line below and provide your AWS account ID  

#env=cdk.Environment(account='123456789012', region='us-east-1'),

# For more information, see https://docs.aws.amazon.com/cdk/latest/guide/environments.html

GoldengateCdkStack(app, "GoldengateCdkStack",
                    description="Goldengate - a template SPA website deployment into AWS with AWSCDK",
                    env=environment
)

app.synth()