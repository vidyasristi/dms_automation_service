from model.InputModel import InputModel
from service.endpoint_service import EndpointService
from service.cleanup_service import CleanUpService
import boto3
import random
import string
import asyncio

client = boto3.client('dms')
endpointService = EndpointService()
cleanUpService = CleanUpService()


def deploy_dms(input: InputModel):
    provisioned_resources = {}
    uniqueId = ''.join(random.choice(string.ascii_lowercase) for i in range(10))
    sourceResponse = endpointService.create_source_endpoint(input, uniqueId, provisioned_resources)
    # targetResponse = create_target_endpoint(input)
    # create_replication_task(input, sourceResponse, targetResponse)
    # print(sourceResponse)
    # print(targetResponse)
    # instanceResponse = await create_replication_instance(input)
    # print(instanceResponse)
    # await asyncio.sleep(10)


def create_replication_instance(input: InputModel):
    return client.create_replication_instance(
        ReplicationInstanceIdentifier='instance' + ''.join(random.choice(string.ascii_lowercase) for i in range(10)),
        AllocatedStorage=input.replicationInstanceDetails.replicationInstanceStorage,
        ReplicationInstanceClass=input.replicationInstanceDetails.replicationInstanceClass,
        VpcSecurityGroupIds=[
            'sg-bee091b5'
        ],
        # AvailabilityZone='string',
        ReplicationSubnetGroupIdentifier='default-vpc-33d7744e',
        MultiAZ=False,
        # EngineVersion='string',
        Tags=generate_tags(input),
        PubliclyAccessible=False
    )


def create_replication_task(input, sourceResponse, targetResponse):
    response = client.create_replication_task(
        ReplicationTaskIdentifier='task' + ''.join(random.choice(string.ascii_lowercase) for i in range(10)),
        SourceEndpointArn=sourceResponse['Endpoint']['EndpointArn'],
        TargetEndpointArn=targetResponse['Endpoint']['EndpointArn'],
        ReplicationInstanceArn=input.replicationInstanceDetails.replicationInstanceArn,
        MigrationType=input.replicationTaskDetails.migrationType,
        TableMappings=input.replicationTaskDetails.tableMappings,
        # ReplicationTaskSettings=input.replicationTaskDetails.replicationTaskSettings,
    )


def create_target_endpoint(input: InputModel):
    letters = string.ascii_lowercase
    random_name = ''.join(random.choice(letters) for i in range(10))
    return client.create_endpoint(
        EndpointIdentifier="target" + random_name,
        EndpointType=input.targetEndpointDetails.endpointType,
        EngineName="postgres",
        DatabaseName=input.targetEndpointDetails.databaseName,
        # ExtraConnectionAttributes=input.targetEndpointDetails.extraConnectionAttributes,
        # CertificateArn='string',
        SslMode='none',
        PostgreSQLSettings={
            'SecretsManagerAccessRoleArn': input.targetEndpointDetails.secretsManagerAccessRoleArn,
            'SecretsManagerSecretId': input.targetEndpointDetails.secretsManagerSecretId
        })
