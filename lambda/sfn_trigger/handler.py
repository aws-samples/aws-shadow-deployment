import os
from datetime import datetime
import json

import boto3

sfn_client = boto3.client("stepfunctions")

STATE_MACHINE_ARN = os.environ.get("STATE_MACHINE_ARN")
WAIT_SECONDS = os.environ.get("WAIT_SECONDS")


def lambda_handler(event, context):

    print(event)

    s3_objects = [
        {
            "bucket": event_record["s3"]["bucket"]["name"],
            "key": event_record["s3"]["object"]["key"],
        }
        for event_record in event["Records"]
        if event_record["s3"] and "tar.gz" in event_record["s3"]["object"]["key"]
    ]

    if s3_objects:
        for record in s3_objects:

            bucket = record["bucket"]
            key = record["key"]
            model_path = f"s3://{bucket}/{key}"

            current_time = datetime.now().strftime("%Y-%m-%d-%H-%M")

            sfn_inputs = {
                "Comment": "Automatically triggered by S3 put item event",
                "model_path": model_path,
                "job_name": f"xgboost-{current_time}",
                "wait_seconds": WAIT_SECONDS,
            }

            _ = sfn_client.start_execution(
                stateMachineArn=STATE_MACHINE_ARN,
                name=current_time,
                input=json.dumps(sfn_inputs),
            )
