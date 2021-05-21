import os
import boto3

ssm = boto3.client("ssm")
sm = boto3.client("sagemaker")

SHADOW_ENDPOINT_SSM = os.environ.get("SHADOW_ENDPOINT_SSM")
PROD_ENDPOINT_SSM = os.environ.get("PROD_ENDPOINT_SSM")


def lambda_handler(event, context):

    print(event)
    output = dict(event)["is_shadow_selected"]["Output"]

    is_shadow_selected = True if 'true' in output else False

    prod_endpoint_name = ssm.get_parameter(Name=PROD_ENDPOINT_SSM)["Parameter"]["Value"]
    shadow_endpoint_name = ssm.get_parameter(Name=SHADOW_ENDPOINT_SSM)["Parameter"][
        "Value"
    ]

    if is_shadow_selected:
        _ = ssm.put_parameter(
            Name=PROD_ENDPOINT_SSM, Value=shadow_endpoint_name, Overwrite=True
        )
        _ = ssm.put_parameter(Name=SHADOW_ENDPOINT_SSM, Value="None", Overwrite=True)
        _ = sm.delete_endpoint(EndpointName=prod_endpoint_name)
    else:
        _ = ssm.put_parameter(Name=SHADOW_ENDPOINT_SSM, Value="None", Overwrite=True)
        _ = sm.delete_endpoint(EndpointName=shadow_endpoint_name)
