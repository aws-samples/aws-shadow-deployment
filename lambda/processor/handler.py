import os
import boto3

sm_runtime = boto3.client("runtime.sagemaker")
ssm = boto3.client("ssm")
ddb = boto3.client("dynamodb")

SHADOW_ENDPOINT_SSM = os.environ.get("SHADOW_ENDPOINT_SSM")
PROD_ENDPOINT_SSM = os.environ.get("PROD_ENDPOINT_SSM")
RESULT_TABLE_DDB = os.environ.get("RESULT_TABLE_DDB")


def prediction(endpointname: str, body: str):
    response = sm_runtime.invoke_endpoint(EndpointName=endpointname, Body=body)
    return float(response["Body"].read().decode("utf-8"))


def update_result(endpointname: str, record: dict, probabilty: float):
    message_id = str(record["message_id"])
    timestamp = str(record["timestamp"])
    data = record["body"][2:].encode().decode()
    label = int(record["body"][:1])
    prediction = 1 if probabilty >= 0.5 else 0
    score = 1 if label == prediction else 0

    item = {
        "MessageId": {"S": message_id},
        "ModelName": {"S": endpointname},
        "TimeStamp": {"N": timestamp},
        "Data": {"S": data},
        "Label": {"N": str(label)},
        "Prediction": {"N": str(prediction)},
        "Probability": {"N": str(probabilty)},
        "Score": {"S": str(score)},
    }

    ddb.put_item(TableName=RESULT_TABLE_DDB, Item=item)


def lambda_handler(event, context):

    print(event)

    records = [
        {
            "body": event_record["body"],
            "timestamp": event_record["attributes"]["SentTimestamp"],
            "message_id": event_record["messageId"],
        }
        for event_record in event["Records"]
        if event_record["body"]
    ]

    prod_endpoint_name = ssm.get_parameter(Name=PROD_ENDPOINT_SSM)["Parameter"]["Value"]
    shadow_endpoint_name = ssm.get_parameter(Name=SHADOW_ENDPOINT_SSM)["Parameter"][
        "Value"
    ]

    if records:
        for record in records:

            body = record["body"][2:].encode().decode()
            prod_probabilty = prediction(prod_endpoint_name, body)

            update_result(prod_endpoint_name, record, prod_probabilty)

            print(prod_probabilty)

            if shadow_endpoint_name != "None":
                shadow_probabilty = prediction(shadow_endpoint_name, body)

                shadow_probabilty = prediction(
                    shadow_endpoint_name, record["body"][2:].encode().decode()
                )

                update_result(shadow_endpoint_name, record, shadow_probabilty)
