import boto3


class CleanUpService:

    def __init__(self):
        self.dms_client = boto3.client('dms')

    def cleanup_resources(self, provisioned_resources: dict):
        for eachKey in provisioned_resources:
            if eachKey in ["sourceCertificateArn"]:
                print("Cleaning up sourceCertificate with arn: " + provisioned_resources[eachKey])
                self.dms_client.delete_certificate(CertificateArn=provisioned_resources[eachKey])

