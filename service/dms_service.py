from model.InputModel import InputModel, DeleteModel
from service.endpoint_service import EndpointService
from service.cleanup_service import CleanUpService
from util.dms_util import generate_tags, populate_resources_dict
from util.exception_util import ProcessingException
from service.replication_service import ReplicationService
import boto3
import random
import string

import uuid

client = boto3.client('dms')
endpointService = EndpointService()
cleanUpService = CleanUpService()
replicationService = ReplicationService()


def deploy_dms(input: InputModel):
    provisioned_resources = {}
    populate_resources_dict(provisioned_resources)
    uniqueId = str(uuid.uuid4())
    try:
        # replicationService.create_replication_instance(input, uniqueId, provisioned_resources)
        endpointService.create_source_endpoint(input, uniqueId, provisioned_resources)
        # endpointService.create_target_endpoint(input, uniqueId, provisioned_resources)
        # replicationService.create_replication_task(input, uniqueId, provisioned_resources)
    except Exception as e:
        raise ProcessingException(provisioned_resources, e)
    return uniqueId


def create_replication_task(input, uniqueId, provisioned_resources):
    response = client.create_replication_task(
        ReplicationTaskIdentifier='task-' + uniqueId,
        SourceEndpointArn=provisioned_resources['sourceEndpointArn'],
        TargetEndpointArn=provisioned_resources['targetEndpointArn'],
        ReplicationInstanceArn=input.replicationInstanceDetails.replicationInstanceArn,
        MigrationType=input.replicationTaskDetails.migrationType,
        TableMappings=input.replicationTaskDetails.tableMappings,
        # ReplicationTaskSettings=input.replicationTaskDetails.replicationTaskSettings,
    )


def delete_dms(deleteInput: DeleteModel):
    cleanUpService.delete_dms_resources(deleteInput)
