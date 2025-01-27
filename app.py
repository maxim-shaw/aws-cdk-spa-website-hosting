#!/usr/bin/env python3
import os
import json

import aws_cdk as cdk

from goldengate_cdk.goldengate_cdk_stack import GoldengateCdkStack


app = cdk.App()

with open("stages.json") as stagesJson:
    stages = json.load(stagesJson)

    if stages and stages.get(os.environ.get("CDK_ENV_VARIABLE")):
        stage = stages.get(os.environ.get("CDK_ENV_VARIABLE"))

        # If you don't specify 'env', this stack will be environment-agnostic.
        # Account/Region-dependent features and context lookups will not work,
        # but a single synthesized template can be deployed anywhere.

        # Uncomment the next line to specialize this stack for the AWS Account
        # and Region that are implied by the current CLI configuration.

        environment = cdk.Environment(
            account=os.environ.get("CDK_DEPLOYMENT_ACCOUNT", os.environ["CDK_DEFAULT_ACCOUNT"]),
            region=os.environ.get("CDK_DEPLOYMENT_REGION", os.environ["CDK_DEFAULT_REGION"]),
        )

        # Uncomment the next line if you know exactly what Account and Region you
        # want to deploy the stack to. */

        #env=cdk.Environment(account='123456789012', region='us-east-1'),

        # For more information, see https://docs.aws.amazon.com/cdk/latest/guide/environments.html

        GoldengateCdkStack(app, "GoldengateCdkStack",
                           description="Goldengate - A template SPA website deployment into AWS with AWSCDK",
                           env=environment,
                           stage=stage
        )
        
app.synth()

# GoldengateCdkStack(app, "GoldengateCdkStack",

#     env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),

#     )

# app.synth()
