import boto3
from model.InputModel import DeleteModel
import botocore
import time


class CleanUpService:

    def __init__(self):
        self.dms_client = boto3.client('dms')

    def cleanup_resources(self, provisioned_resources: dict):
        for eachKey in provisioned_resources:
            if provisioned_resources[eachKey] and eachKey in ["sourceCertificateArn", "targetCertificateArn"]:
                print("Cleaning up certificate with arn: " + provisioned_resources[eachKey])
                self.dms_client.delete_certificate(CertificateArn=provisioned_resources[eachKey])
                isCertificateDeleted = False
                while not isCertificateDeleted:
                    try:
                        self.dms_client.describe_certificates(
                            Filters=[
                                {
                                    'Name': 'certificate-arn',
                                    'Values': [provisioned_resources[eachKey]]
                                }
                            ])
                        time.sleep(3)
                    except botocore.exceptions.ClientError as e:
                        print("Successfully deleted certificate with arn: " + provisioned_resources[eachKey])
                        isCertificateDeleted = True
            elif provisioned_resources[eachKey] and eachKey in ["sourceEndpointArn", "targetEndpointArn"]:
                print("Cleaning up endpoint with arn: " + provisioned_resources[eachKey])
                self.dms_client.delete_endpoint(EndpointArn=provisioned_resources[eachKey])
                isEndpointDeleted = False
                while not isEndpointDeleted:
                    try:
                        self.dms_client.describe_endpoints(
                            Filters=[
                                {
                                    'Name': 'endpoint-arn',
                                    'Values': [provisioned_resources[eachKey]]
                                }
                            ])
                        time.sleep(5)
                    except botocore.exceptions.ClientError as e:
                        print("Successfully deleted endpoint with arn: " + provisioned_resources[eachKey])
                        isEndpointDeleted = True
            elif provisioned_resources[eachKey] and eachKey in ['replicationTaskArn']:
                print('Cleaning up replication task with arn: ' + provisioned_resources[eachKey])
                self.dms_client.delete_replication_task(ReplicationTaskArn=provisioned_resources[eachKey])
                isTaskDeleted = False
                while not isTaskDeleted:
                    try:
                        self.dms_client.describe_replication_tasks(
                            Filters=[
                                {
                                    'Name': 'replication-task-arn',
                                    'Values': [provisioned_resources[eachKey]]
                                }
                            ])
                        time.sleep(5)
                    except botocore.exceptions.ClientError as e:
                        print("Successfully deleted replication task with arn: " + provisioned_resources[eachKey])
                        isTaskDeleted = True
            elif provisioned_resources[eachKey] and eachKey in ['replicationInstanceArn']:
                print('Cleaning up replication instance with arn: ' + provisioned_resources[eachKey])
                self.dms_client.delete_replication_instance(ReplicationInstanceArn=provisioned_resources[eachKey])
                isInstanceDeleted = False
                while not isInstanceDeleted:
                    try:
                        self.dms_client.describe_replication_instances(
                            Filters=[
                                {
                                    'Name': 'replication-instance-arn',
                                    'Values': [provisioned_resources[eachKey]]
                                }])
                        time.sleep(5)
                    except botocore.exceptions.ClientError as e:
                        print("Successfully deleted replication instance with arn: " + provisioned_resources[eachKey])
                        isInstanceDeleted = True

    def delete_dms_resources(self, deleteModel: DeleteModel):
        provisioned_resources = {}
        if deleteModel.uniqueId:
            try:
                response = self.dms_client.describe_replication_tasks(
                    Filters=[
                        {
                            'Name': 'replication-task-id',
                            'Values': ['task-' + deleteModel.uniqueId]
                        }
                    ])
                provisioned_resources['replicationTaskArn'] = response['ReplicationTasks'][0]['ReplicationTaskArn']
            except botocore.exceptions.ClientError as e:
                print("Exception occurred while trying to delete replication task: " + str(e))

            try:
                response = self.dms_client.describe_endpoints(
                    Filters=[
                        {
                            'Name': 'endpoint-type',
                            'Values': ['source']
                        },
                        {
                            'Name': 'endpoint-id',
                            'Values': ['source-' + deleteModel.uniqueId]
                        }])
                provisioned_resources['sourceEndpointArn'] = response['Endpoints'][0]['EndpointArn']
                provisioned_resources['sourceCertificateArn'] = response['Endpoints'][0]['CertificateArn']

            except botocore.exceptions.ClientError as e:
                print("Exception occurred while trying to delete source endpoint: " + str(e))

            try:
                response = self.dms_client.describe_endpoints(
                    Filters=[
                        {
                            'Name': 'endpoint-type',
                            'Values': ['target']
                        },
                        {
                            'Name': 'endpoint-id',
                            'Values': ['target-' + deleteModel.uniqueId]
                        }])
                provisioned_resources['targetEndpointArn'] = response['Endpoints'][0]['EndpointArn']
                provisioned_resources['targetCertificateArn'] = response['Endpoints'][0]['CertificateArn']
            except botocore.exceptions.ClientError as e:
                print("Exception occurred while trying to delete target endpoint: " + str(e))

            try:
                response = self.dms_client.describe_replication_instances(
                    Filters=[
                        {
                            'Name': 'replication-instance-id',
                            'Values': ['instance-' + deleteModel.uniqueId]
                        }])
                provisioned_resources['replicationInstanceArn'] = response['ReplicationInstances'][0][
                    'ReplicationInstanceArn']
            except botocore.exceptions.ClientError as e:
                print("Exception occurred while trying to delete replication instance: " + str(e))

        print("Built provisioned_resources: " + str(provisioned_resources))
        self.cleanup_resources(provisioned_resources)
