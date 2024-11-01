import aws_cdk as core
import aws_cdk.assertions as assertions

from goldengate_cdk.goldengate_cdk_stack import GoldengateCdkStack

# example tests. To run these tests, uncomment this file along with the example
# resource in goldengate_cdk/goldengate_cdk_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = GoldengateCdkStack(app, "goldengate-cdk")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
