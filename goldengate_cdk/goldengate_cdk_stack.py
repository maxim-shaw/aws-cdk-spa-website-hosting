from aws_cdk import (
    aws_s3 as s3,
    aws_iam as iam,
    aws_route53 as route53,
    aws_route53_targets as targets,
    aws_certificatemanager as acm,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_s3_deployment as s3_deployment,
    RemovalPolicy,
    # Duration,
    Stack,
    Names,
    # aws_sqs as sqs,
)
from constructs import Construct

from EnvConfig.env_constants import ConstantsNamespace

class GoldengateCdkStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Public variables
        self.constants = ConstantsNamespace()
        self.construct = scope
        self.website_bucket = None
        self.certificate = None
        self.distribution = None

        #Instance/private variables
        self.__domain_certificate_arn = self.constants.DOMAIN_CERTIFICATE_ARN
        self._website_domain_name = self.constants.DOMAIN_NAME

        self._build_website()
    
    def _build_website(self):
        # Create the S3 bucket for the site contents
        self.__create_website_bucket()

        # Get the hosted zone based on the provided domain name
        hosted_zone = self.__get_hosted_zone()

        # Get an existing or create a new certificate for the site domain
        self.__create_certificate(hosted_zone)

        # create the cloud front distribution
        self.__create_cloudfront_distribution()

        # Create a Route53 record for public access
        self.__create_route53_record(hosted_zone)


    def __create_website_bucket(self):

        # Create S3 bucket for the goldengate website
        website_bucket_name = self.constants.WEBSITE_BUCKET_NAME

        self.website_bucket = s3.Bucket(
            self,
            self.constants.WEBSITE_BUCKET_NAME,
            public_read_access=True,          
            block_public_access=s3.BlockPublicAccess.BLOCK_ACLS,
            access_control=s3.BucketAccessControl.BUCKET_OWNER_FULL_CONTROL,
            bucket_name=website_bucket_name,
            encryption=s3.BucketEncryption.S3_MANAGED,
            auto_delete_objects=True,
            removal_policy=RemovalPolicy.DESTROY
        )

        self.website_bucket.add_to_resource_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["s3:GetObject"],
                resources=[
                    self.website_bucket.bucket_arn,
                    self.website_bucket.arn_for_objects("*")],
                principals=[iam.AnyPrincipal()]
        ))

        s3_deployment.BucketDeployment(
            self, "GoldengateWebsiteDeployment",
            sources=[s3_deployment.Source.asset("./website-dist")],
            destination_bucket=self.website_bucket
        )

    def __get_hosted_zone(self):
        return route53.HostedZone.from_hosted_zone_attributes(
            self,
            "hosted_zone",
            zone_name=self.constants.HOSTED_ZONE_NAME,
            hosted_zone_id=self.constants.HOSTED_ZONE_ID
        )
    
    def __create_certificate(self, hosted_zone):
        if self.__domain_certificate_arn:
            # If certificate arn is provided, import the certificate
            self.certificate = acm.Certificate.from_certificate_arn(
                self,
                "site_certificate",
                certificate_arn=self.__domain_certificate_arn,
            )
        else:
            # If certificate arn is not provided, create a new one.
            # ACM certificates that are used with CloudFront must be in
            # the us-east-1 region.
            self.certificate = acm.DnsValidatedCertificate(
                self,
                "site_certificate",
                domain_name=self._website_domain_name,
                hosted_zone=hosted_zone,
                region="us-east-1",
            )

    def __create_cloudfront_distribution(self):
        """Create a cloudfront distribution with a private bucket as the origin"""
        self.distribution = cloudfront.Distribution(
            self,
            "cloudfront_distribution",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3Origin(self.website_bucket),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
            ),
            domain_names=[self._website_domain_name],
            certificate=self.certificate,
            default_root_object="index.html",
        )

    def __create_route53_record(self, hosted_zone):
        route53.ARecord(
            self,
            "goldengate-record",
            record_name=self._website_domain_name,
            zone=hosted_zone,
            target=route53.RecordTarget.from_alias(
                targets.CloudFrontTarget(self.distribution)
            )
        )