from model.InputModel import InputModel


def generate_tags(input: InputModel):
    if not input.tags.ApplicationShortName or not input.tags.AppCode or not input.tags.AssetId:
        raise Exception('Tags required are not provided in input.Cannot continue forward.')
    return [
        {'Key': 'ApplicationShortName', 'Value': input.tags.ApplicationShortName},
        {'Key': 'AppCode', 'Value': input.tags.AppCode},
        {'Key': 'AssetId', 'Value': input.tags.AssetId}
    ]


def populate_resources_dict(provisioned_resources):
    provisioned_resources['replicationTaskArn'] = None
    provisioned_resources['replicationInstanceArn'] = None
    provisioned_resources['sourceEndpointArn'] = None
    provisioned_resources['targetEndpointArn'] = None
    provisioned_resources['sourceCertificateArn'] = None
    provisioned_resources['targetCertificateArn'] = None
