import os
import csv
import random
import boto3

sqs = boto3.client("sqs")
s3 = boto3.client("s3")

QUEUE_URL = os.environ.get("QUEUE_URL")
DATA_URL = os.environ.get("DATA_URL")

BUCKET = DATA_URL.split("/")[2]
KEY = DATA_URL.split("/", 3)[-1]


def lambda_handler(event, context):

    s3.download_file(BUCKET, KEY, "/tmp/test.csv")

    with open("/tmp/test.csv") as f:
        reader = csv.reader(f)
        chosen_row = random.choice(list(reader))
        chosen_row = ",".join([str(elem) for elem in chosen_row])

    _ = sqs.send_message(QueueUrl=QUEUE_URL, MessageBody=(chosen_row))
