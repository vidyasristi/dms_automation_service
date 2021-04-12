import boto3
import botocore
import shutil
import os
import time
from pathlib import Path
import logging
from os import path
from util.exception_util import ProcessingException
from util.dms_util import generate_tags

from model.InputModel import InputModel, EngineNameEnum

log = logging.getLogger('root')


class EndpointService:

    def __init__(self):
        self.dms_client = boto3.client('dms')
        self.s3 = boto3.resource('s3')
        self.s3_client = boto3.client('s3')

    def create_source_certificate(self, input: InputModel, provisioned_resources, uniqueId):
        BUCKET_NAME = 'dms-db-certificates'  # replace with your bucket name
        FOLDER = input.tags.AppCode + '/' + input.sourceEndpointDetails.databaseName + '/'
        KEY = self.get_s3_certificate_name(BUCKET_NAME, FOLDER)  # 'rds-ca-2019-root.pem'
        DEST_FOLDER = '/resources/source_cert/' + input.sourceEndpointDetails.databaseName
        DEST_FILE = 'resources/source_cert/' + input.sourceEndpointDetails.databaseName + '/' + KEY
        log.info("Trying to get certificate from: " + BUCKET_NAME + "/" + FOLDER + KEY)

        Path(os.getcwd() + DEST_FOLDER).mkdir(parents=True, exist_ok=True)
        self.s3.Bucket(BUCKET_NAME).download_file(FOLDER + KEY, DEST_FILE)

        current_path = path.abspath(path.join(path.dirname(__file__), os.pardir))
        log.info("Current path is " + current_path)
        response = None
        with open(os.path.join(current_path, DEST_FILE), 'r', newline='\r\n') as inputCert:
            certificate = inputCert.read()

            response = self.dms_client.import_certificate(
                CertificateIdentifier='source-certificate-' + uniqueId,
                CertificatePem=certificate,
                Tags=generate_tags(input))
        provisioned_resources['sourceCertificateArn'] = response['Certificate']['CertificateArn']
        shutil.rmtree('resources/source_cert/' + input.sourceEndpointDetails.databaseName, ignore_errors=True)

    def create_target_certificate(self, input: InputModel, provisioned_resources, uniqueId):
        BUCKET_NAME = 'dms-db-certificates'  # replace with your bucket name
        FOLDER = input.tags.AppCode + '/' + input.targetEndpointDetails.databaseName + '/'
        KEY = self.get_s3_certificate_name(BUCKET_NAME, FOLDER)
        DEST_FOLDER = '/resources/target_cert/' + input.targetEndpointDetails.databaseName
        DEST_FILE = 'resources/target_cert/' + input.targetEndpointDetails.databaseName + '/' + KEY
        log.info("Trying to get certificate from: " + BUCKET_NAME + "/" + FOLDER + KEY)

        Path(os.getcwd() + DEST_FOLDER).mkdir(parents=True, exist_ok=True)
        self.s3.Bucket(BUCKET_NAME).download_file(FOLDER + KEY, DEST_FILE)

        current_path = path.abspath(path.join(path.dirname(__file__), os.pardir))
        log.info("Current path is " + current_path)
        response = None
        with open(os.path.join(current_path, DEST_FILE), 'r', newline='\r\n') as inputCert:
            certificate = inputCert.read()

            response = self.dms_client.import_certificate(
                CertificateIdentifier='target-certificate-' + uniqueId,
                CertificatePem=certificate,
                Tags=generate_tags(input))
        provisioned_resources['targetCertificateArn'] = response['Certificate']['CertificateArn']
        shutil.rmtree('resources/target_cert/' + input.targetEndpointDetails.databaseName,
                      ignore_errors=True)  # Delete when s3 download fails in processingException

    def create_source_endpoint(self, input: InputModel, uniqueId: str, provisioned_resources: dict):
        self.create_source_certificate(input, provisioned_resources, uniqueId)

        opts = {}
        self.populate_source_endpoint_options(input, opts)

        sourceEndpointResponse = self.dms_client.create_endpoint(
            EndpointIdentifier="source-" + uniqueId,
            EndpointType=input.sourceEndpointDetails.endpointType,
            EngineName=input.sourceEndpointDetails.engineName,
            DatabaseName=input.sourceEndpointDetails.databaseName,
            CertificateArn=provisioned_resources['sourceCertificateArn'],
            SslMode='verify-full', Tags=generate_tags(input), **opts)
        provisioned_resources['sourceEndpointArn'] = sourceEndpointResponse['Endpoint']['EndpointArn']
        self.test_endpoint_connectivity(provisioned_resources['replicationInstanceArn'],
                                        provisioned_resources['sourceEndpointArn'])

    def create_target_endpoint(self, input: InputModel, uniqueId: str, provisioned_resources: dict):
        self.create_target_certificate(input, provisioned_resources, uniqueId)

        opts = {}
        self.populate_target_endpoint_options(input, opts)

        targetEndpointResponse = self.dms_client.create_endpoint(
            EndpointIdentifier="target-" + uniqueId,
            EndpointType=input.targetEndpointDetails.endpointType,
            EngineName=input.targetEndpointDetails.engineName,
            DatabaseName=input.targetEndpointDetails.databaseName,
            CertificateArn=provisioned_resources['targetCertificateArn'],
            SslMode='verify-full',
            Tags=generate_tags(input),
            **opts)
        provisioned_resources['targetEndpointArn'] = targetEndpointResponse['Endpoint']['EndpointArn']
        self.test_endpoint_connectivity(provisioned_resources['replicationInstanceArn'],
                                        provisioned_resources['sourceEndpointArn'])

    def test_endpoint_connectivity(self, instanceArn, endpointArn):
        response = self.dms_client.test_connection(ReplicationInstanceArn=instanceArn, EndpointArn=endpointArn)
        isEndpointConnectivitySuccessful = False
        while not isEndpointConnectivitySuccessful:
            response = self.dms_client.describe_connections(
                Filters=[
                    {
                        'Name': 'endpoint-arn',
                        'Values': [endpointArn]
                    }])
            if response['Connections'][0]['Status'] == 'testing':
                time.sleep(5)
            elif response['Connections'][0]['Status'] == 'successful':
                isEndpointConnectivitySuccessful = True
            else:
                raise Exception('Endpoint connectivity for Arn: ' + endpointArn + ", failed with status: " +
                                response['Connections'][0]['Status'] + ", failureMessage: " +
                                response['Connections'][0]['LastFailureMessage'])

    def populate_source_endpoint_options(self, input: InputModel, opts: dict):
        if input.sourceEndpointDetails.extraConnectionAttributes and input.sourceEndpointDetails.extraConnectionAttributes != "":
            opts['ExtraConnectionAttributes'] = input.sourceEndpointDetails.extraConnectionAttributes
        if input.sourceEndpointDetails.engineName and input.sourceEndpointDetails.engineName is EngineNameEnum.postgres:
            opts['PostgreSQLSettings'] = {}
            opts['PostgreSQLSettings'][
                'SecretsManagerAccessRoleArn'] = input.sourceEndpointDetails.secretsManagerAccessRoleArn
            opts['PostgreSQLSettings']['SecretsManagerSecretId'] = input.sourceEndpointDetails.secretsManagerSecretId

    def populate_target_endpoint_options(self, input: InputModel, opts: dict):
        if input.targetEndpointDetails.extraConnectionAttributes and input.targetEndpointDetails.extraConnectionAttributes != "":
            opts['ExtraConnectionAttributes'] = input.targetEndpointDetails.extraConnectionAttributes
        if input.targetEndpointDetails.engineName and input.targetEndpointDetails.engineName is EngineNameEnum.postgres:
            opts['PostgreSQLSettings'] = {}
            opts['PostgreSQLSettings'][
                'SecretsManagerAccessRoleArn'] = input.targetEndpointDetails.secretsManagerAccessRoleArn
            opts['PostgreSQLSettings']['SecretsManagerSecretId'] = input.targetEndpointDetails.secretsManagerSecretId

    def get_s3_certificate_name(self, BUCKET_NAME, FOLDER):
        response = self.s3_client.list_objects_v2(Bucket=BUCKET_NAME, Prefix=FOLDER)
        key = response['Contents'][0]['Key']
        return key.split('/')[-1]
