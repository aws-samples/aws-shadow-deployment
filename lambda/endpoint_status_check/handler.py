import os
import boto3

sm_client = boto3.client("sagemaker")


def lambda_handler(event, context):

    print(event)

    shadow_endpont_name = dict(event)["job_name"]

    # 'OutOfService'|'Creating'|'Updating'|'SystemUpdating'|'RollingBack'|'InService'|'Deleting'|'Failed'
    return sm_client.describe_endpoint(EndpointName=shadow_endpont_name)[
        "EndpointStatus"
    ]
