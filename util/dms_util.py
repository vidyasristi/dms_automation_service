from model.InputModel import InputModel


def generate_tags(input: InputModel):
    return [
        {'Key': 'ApplicationShortName', 'Value': input.tags.ApplicationShortName},
        {'Key': 'AppCode', 'Value': input.tags.AppCode},
        {'Key': 'AssetId', 'Value': input.tags.AssetId}
    ]
