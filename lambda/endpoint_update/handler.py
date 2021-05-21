import os
import boto3

ssm = boto3.client("ssm")

SHADOW_ENDPOINT_SSM = os.environ.get("SHADOW_ENDPOINT_SSM")


def lambda_handler(event, context):

    print(event)

    shadow_endpont_name = dict(event)["job_name"]

    response = ssm.put_parameter(
        Name=SHADOW_ENDPOINT_SSM, Value=shadow_endpont_name, Overwrite=True
    )
