import os
import time
from decimal import Decimal
import boto3
from boto3.dynamodb.conditions import Key, Attr

SHADOW_ENDPOINT_SSM = os.environ.get("SHADOW_ENDPOINT_SSM")
PROD_ENDPOINT_SSM = os.environ.get("PROD_ENDPOINT_SSM")
RESULT_TABLE_DDB = os.environ.get("RESULT_TABLE_DDB")

ddb = boto3.resource("dynamodb")
ssm = boto3.client("ssm")


def lambda_handler(event, context):

    prod_model_name = ssm.get_parameter(Name=PROD_ENDPOINT_SSM)["Parameter"]["Value"]
    shadow_model_name = ssm.get_parameter(Name=SHADOW_ENDPOINT_SSM)["Parameter"][
        "Value"
    ]

    Table = ddb.Table(RESULT_TABLE_DDB)

    shadow_items = Table.scan(FilterExpression=Attr("ModelName").eq(shadow_model_name))
    shadow_ls = [item["MessageId"] for item in shadow_items["Items"]]
    items = Table.scan(FilterExpression=Attr("MessageId").is_in(shadow_ls))
    prod_ls = [
        item["MessageId"]
        for item in items["Items"]
        if item["ModelName"] == prod_model_name
    ]
    ls = list(set(shadow_ls) & set(prod_ls))

    shadow_score = 0
    prod_score = 0

    for item in items["Items"]:
        ModelName = item["ModelName"]
        MessageId = item["MessageId"]
        Score = item["Score"]
        if MessageId in ls:
            if ModelName == shadow_model_name:
                shadow_score += int(Score)
            elif ModelName == prod_model_name:
                prod_score += int(Score)
            else:
                pass

    return {
        "shadow_score": f"{shadow_score}/{len(ls)}",
        "prod_score": f"{prod_score}/{len(ls)}",
    }
