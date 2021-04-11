import string
import random

import boto3
import botocore
import os
from pathlib import Path
import logging
from os import path
from util.ProcessingException import ProcessingException

from model.InputModel import InputModel

log = logging.getLogger('root')


class EndpointService:

    def __init__(self):
        self.dms_client = boto3.client('dms')
        self.s3 = boto3.resource('s3')

    def create_source_certificate(self, input: InputModel, provisioned_resources, uniqueId):
        BUCKET_NAME = 'dms-db-certificates'  # replace with your bucket name
        KEY = 'gd9/source-db/rds-ca-2019-root.pem'  # replace with your object key
        log.info("Trying to get certificate from: " + BUCKET_NAME + "/" + KEY)

        Path(os.getcwd() + "/resources/source_cert/source-db").mkdir(parents=True, exist_ok=True)
        try:
            self.s3.Bucket(BUCKET_NAME).download_file(KEY, 'resources/source_cert/source-db/cert.pem')
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                log.error("The object does not exist.")
            else:
                raise Exception('Error downloading source certificate from S3')

        current_path = path.abspath(path.join(path.dirname(__file__), os.pardir))
        log.info("Current path is " + current_path)
        response = None
        certificate = None
        with open(os.path.join(current_path, "resources/source_cert/source-db/cert.pem"), 'r',
                  newline='\r\n') as inputCert:
            certificate = inputCert.read()

            response = self.dms_client.import_certificate(
                CertificateIdentifier='source-certificate-' + uniqueId,
                CertificatePem=certificate
                # Tags=[
                #     {
                #         'Key': 'string',
                #         'Value': 'string'
                #     },
                # ]
            )
            log.info(response)
            provisioned_resources['sourceEndpoint'] = {}
            provisioned_resources['sourceCertificateArn'] = response['Certificate']['CertificateArn']

    def create_source_endpoint(self, input: InputModel, uniqueId: str, provisioned_resources: dict):

        self.create_source_certificate(input, provisioned_resources, uniqueId)

        # response = self.client.import_certificate(
        #     CertificateIdentifier='string',
        #     CertificatePem='string',
        #     CertificateWallet=b'bytes',
        #     Tags=[
        #         {
        #             'Key': 'string',
        #             'Value': 'string'
        #         },
        #     ]
        # )
        #
        try:
            return self.dms_client.create_endpoint(
                EndpointIdentifier="source" + uniqueId,
                EndpointType=input.sourceEndpointDetails.endpointType,
                EngineName=input.sourceEndpointDetails.engineName,
                DatabaseName=input.sourceEndpointDetails.databaseName,
                ExtraConnectionAttributes=None,
                CertificateArn=provisioned_resources['sourceCertificateArn'],
                SslMode='verify-full',
                PostgreSQLSettings={
                    'SecretsManagerAccessRoleArn': input.sourceEndpointDetails.secretsManagerAccessRoleArn,
                    'SecretsManagerSecretId': input.sourceEndpointDetails.secretsManagerSecretId
                })
        except Exception as e:
            print("Am inside catch")
            raise ProcessingException(provisioned_resources)
