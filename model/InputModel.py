from enum import Enum
from typing import Optional

from pydantic import BaseModel


class EndpointTypeEnum(str, Enum):
    source = "source"
    target = "target"


class EngineNameEnum(str, Enum):
    aurora = 'aurora'
    oracle = 'oracle'
    postgres = 'postgres'
    aurora_postgresql = 'aurora-postgresql'
    sybase = 'sybase'


class MigrationTypeEnum(str, Enum):
    full_load = 'full-load'
    cdc = 'cdc'
    full_load_cdc = 'full-load-and-cdc'


class SourceEndpointModel(BaseModel):
    endpointType: EndpointTypeEnum = EndpointTypeEnum.source
    engineName: EngineNameEnum
    databaseName: str
    extraConnectionAttributes: Optional[str]
    secretsManagerAccessRoleArn: str
    secretsManagerSecretId: str


class TargetEndpointModel(BaseModel):
    endpointType: EndpointTypeEnum = EndpointTypeEnum.target
    engineName: EngineNameEnum
    databaseName: str
    extraConnectionAttributes: Optional[str]
    secretsManagerAccessRoleArn: str
    secretsManagerSecretId: str


class ReplicationInstanceModel(BaseModel):
    replicationInstanceArn: Optional[str]
    replicationInstanceClass: Optional[str] = "dms.t2.micro"
    replicationInstanceStorage: Optional[int] = 20


class ReplicationTaskModel(BaseModel):
    tableMappings: str
    migrationType: MigrationTypeEnum
    replicationTaskSettings: Optional[str]


class TagsModel(BaseModel):
    ApplicationShortName: str
    AppCode: str
    AssetId: str


class InputModel(BaseModel):
    sourceEndpointDetails: SourceEndpointModel
    targetEndpointDetails: TargetEndpointModel
    replicationTaskDetails: ReplicationTaskModel
    replicationInstanceDetails: ReplicationInstanceModel
    tags: TagsModel
