from model.InputModel import *
import boto3
import random
import string

client = boto3.client('dms')


def deploy_dms(input: InputModel):
    sourceResponse = create_source_endpoint(input)
    targetResponse = create_target_endpoint(input)

    create_replication_task(input, sourceResponse, targetResponse)
    print(sourceResponse)
    print(targetResponse)


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


def create_source_endpoint(input: InputModel):
    letters = string.ascii_lowercase
    random_name = ''.join(random.choice(letters) for i in range(10))
    return client.create_endpoint(
        EndpointIdentifier="source" + random_name,
        EndpointType=input.sourceEndpointDetails.endpointType,
        EngineName="postgres",
        DatabaseName=input.sourceEndpointDetails.databaseName,
        # ExtraConnectionAttributes=input.sourceEndpointDetails.extraConnectionAttributes,
        # CertificateArn='string',
        SslMode='none',
        PostgreSQLSettings={
            'SecretsManagerAccessRoleArn': input.sourceEndpointDetails.secretsManagerAccessRoleArn,
            'SecretsManagerSecretId': input.sourceEndpointDetails.secretsManagerSecretId
        })


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
