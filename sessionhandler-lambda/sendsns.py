import json
import boto3
import os
import time

def respond(err, res=None):
    return {
        'statusCode': '400' if err else '200',
        'body': err.message if err else res,
        'headers': {
            'Content-Type': 'application/json',
        },
    }

def lambda_handler(event, context):
    try:
        msg = {}
        client = boto3.client('sns')
        response = client.publish(
            TargetArn='arn:aws:sns:ap-southeast-2:882607831196:sssalim-api-gateway',
            Message=json.dumps({'default': json.dumps(event)}),
            MessageStructure='json'
        )
        return respond(None,"Thank You ! We will notify guest")
    except Exception as e:
        print(e)
        print("Error adjusting state")
        raise e
