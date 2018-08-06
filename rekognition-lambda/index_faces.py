from __future__ import print_function

import boto3
from decimal import Decimal
import json
import urllib
import os

print('Loading function')

dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')
rekognition = boto3.client('rekognition')

FACE_COLLECTON = os.environ["FACE_COLLECTON"]
FACE_DDB_TABLE = os.environ["FACE_DDB_TABLE"]

def index_faces(bucket, key, collection_id=FACE_COLLECTON):
    response = rekognition.index_faces(
        Image={"S3Object":
            {"Bucket": bucket,
            "Name": key}},
            CollectionId=collection_id)
    return response

def update_index(item, table_name=FACE_DDB_TABLE):
    table = dynamodb.Table(table_name)
    return table.put_item(Item=item)

def lambda_handler(event, context):
    # Get the object from the event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.unquote_plus(
        event['Records'][0]['s3']['object']['key'].encode('utf8'))

    try:
        # Calls Amazon Rekognition IndexFaces API to detect faces in S3 object
        # to index faces into specified collection
        response = index_faces(bucket, key)
        # Commit faceId and full name object metadata to DynamoDB
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            s3_response = s3.head_object(Bucket=bucket,Key=key)
            response = update_index({
                'RekognitionId': response['FaceRecords'][0]['Face']['FaceId'],
                'FullName': s3_response['Metadata']['fullname'],
                'Bucket': bucket,
                'Key': key,
            })
        # Print response to console
        print('index face', bucket, key, response)
        return response['ResponseMetadata']['HTTPStatusCode']
    except Exception as ex:
        print("Error processing object {} from bucket {}: {}".format(key, bucket, ex))
        raise ex
