from pydantic import BaseModel
from typing import Optional
from enum import Enum


class EndpointTypeEnum(str, Enum):
    source = "source"
    target = "target"


class EngineNameEnum(str, Enum):
    aurora = "aurora"


class MigrationTypeEnum(str, Enum):
    full_load = 'full-load'
    cdc = 'cdc'
    full_load_cdc = 'full-load-and-cdc'


class SourceEndpointModel(BaseModel):
    endpointType: EndpointTypeEnum = EndpointTypeEnum.source
    engineName: EngineNameEnum
    serverName: str
    databaseName: str
    extraConnectionAttributes: Optional[str]
    port: int
    secretsManagerAccessRoleArn: str
    secretsManagerSecretId: str


class TargetEndpointModel(BaseModel):
    endpointType: EndpointTypeEnum = EndpointTypeEnum.target
    engineName: EngineNameEnum
    serverName: str
    databaseName: str
    extraConnectionAttributes: Optional[str]
    port: int
    secretsManagerAccessRoleArn: str
    secretsManagerSecretId: str


class ReplicationInstanceModel(BaseModel):
    replicationInstanceArn: str


class ReplicationTaskModel(BaseModel):
    tableMappings: str
    migrationType: MigrationTypeEnum
    replicationTaskSettings: Optional[str]


class InputModel(BaseModel):
    sourceEndpointDetails: SourceEndpointModel
    targetEndpointDetails: TargetEndpointModel
    replicationTaskDetails: ReplicationTaskModel
    replicationInstanceDetails: ReplicationInstanceModel
