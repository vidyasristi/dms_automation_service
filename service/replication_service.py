import boto3
import botocore
from model.InputModel import InputModel
from util.dms_util import generate_tags
import time


class ReplicationService:

    def __init__(self):
        self.dms_client = boto3.client('dms')
        self.s3 = boto3.resource('s3')

    def create_replication_instance(self, input: InputModel, uniqueId, provisioned_resources):
        if input.replicationInstanceDetails.replicationInstanceArn:
            provisioned_resources['replicationInstanceArn'] = input.replicationInstanceDetails.replicationInstanceArn
        else:
            instanceResponse = self.dms_client.create_replication_instance(
                ReplicationInstanceIdentifier='instance-' + uniqueId,
                AllocatedStorage=input.replicationInstanceDetails.replicationInstanceStorage,
                ReplicationInstanceClass=input.replicationInstanceDetails.replicationInstanceClass,
                VpcSecurityGroupIds=['sg-bee091b5'],
                # AvailabilityZone='string',
                ReplicationSubnetGroupIdentifier='default-vpc-33d7744e',
                MultiAZ=False,
                EngineVersion='3.4.4',
                Tags=generate_tags(input),
                PubliclyAccessible=False)

            print(instanceResponse)
            provisioned_resources['replicationInstanceArn'] = instanceResponse['ReplicationInstance'][
                'ReplicationInstanceArn']
            isInstanceUsable = False
            while not isInstanceUsable:
                response = self.dms_client.describe_replication_instances(
                    Filters=[
                        {
                            'Name': 'replication-instance-arn',
                            'Values': [provisioned_resources['replicationInstanceArn']]
                        }])
                if response['ReplicationInstances'][0]['ReplicationInstanceStatus'] == 'creating':
                    time.sleep(5)
                elif response['ReplicationInstances'][0]['ReplicationInstanceStatus'] == 'available':
                    isInstanceUsable = True
                else:
                    raise Exception('Unnable to create replication instance. Last known status of instance: ' +
                                    provisioned_resources['replicationInstanceArn'] + ', status: ' +
                                    response['ReplicationInstances'][0]['ReplicationInstanceStatus'])

    def create_replication_task(self, input, uniqueId, provisioned_resources):
        opts = {}
        self.populate_task_options(input, opts)
        response = self.dms_client.create_replication_task(
            ReplicationTaskIdentifier='task-' + uniqueId,
            SourceEndpointArn=provisioned_resources['sourceEndpointArn'],
            TargetEndpointArn=provisioned_resources['targetEndpointArn'],
            ReplicationInstanceArn=provisioned_resources['replicationInstanceArn'],
            MigrationType=input.replicationTaskDetails.migrationType,
            TableMappings=input.replicationTaskDetails.tableMappings,
            Tags=generate_tags(input),
            **opts)
        provisioned_resources['replicationTaskArn'] = response['ReplicationTask']['ReplicationTaskArn']
        isTaskCreated = False
        while not isTaskCreated:
            response = self.dms_client.describe_replication_tasks(
                Filters=[
                    {
                        'Name': 'replication-task-arn',
                        'Values': [provisioned_resources['replicationTaskArn']]
                    }])
            if response['ReplicationTasks'][0]['Status'] in ['creating', 'modifying', 'starting']:
                time.sleep(5)
            elif response['ReplicationTasks'][0]['Status'] in ['ready']:
                startResponse = self.dms_client.start_replication_task(
                    ReplicationTaskArn=provisioned_resources['replicationTaskArn'],
                    StartReplicationTaskType='start-replication')
                isTaskCreated = True
            else:
                raise Exception('Error starting replication task: ' + provisioned_resources[
                    'replicationTaskArn'] + ", last know status: " + response['ReplicationTasks'][0]['Status'])

    def populate_task_options(self, input: InputModel, opts: dict):
        if input.replicationTaskDetails.replicationTaskSettings:
            opts['ReplicationTaskSettings'] = input.replicationTaskDetails.replicationTaskSettings
