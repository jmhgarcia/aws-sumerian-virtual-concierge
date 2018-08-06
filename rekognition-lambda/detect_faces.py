# detect face against rekognition stack
# see: https://aws.amazon.com/blogs/machine-learning/build-your-own-face-recognition-service-using-amazon-rekognition/

from __future__ import print_function

import boto3
import urllib
import time
import datetime
import json
import os

print('Loading function')

rekognition = boto3.client('rekognition')
cloudwatch = boto3.client('cloudwatch')
dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')
sns = boto3.client('sns')

# TODO: Pull these from enviornment variables
FACE_COLLECTON = os.environ["FACE_COLLECTON"]
FACE_THRESHOLD = int(os.getenv("FACE_THRESHOLD", 75))
FACE_URL_TTL = int(os.getenv("FACE_THRESHOLD", 3600))
FACE_DDB_TABLE = os.environ["FACE_DDB_TABLE"]
FACE_TOPIC_ARN = os.environ["FACE_TOPIC_ARN"]

def push_to_cloudwatch(name, value, timestamp=time.time()):
    try:
        metric_timestamp = datetime.datetime.fromtimestamp(timestamp)
        response = cloudwatch.put_metric_data(
            Namespace='string',
            MetricData=[
                {
                    'MetricName': name,
                    'Timestamp': metric_timestamp,
                    'Value': value,
                    'Unit': 'Percent'
                },
            ]
        )
        #print("Metric pushed: {}".format(response))
    except Exception as ex:
        print("Unable to push to cloudwatch e: {}".format(ex))
        return True

def get_signed_url(bucket, key, ttl=FACE_URL_TTL):
    return s3.generate_presigned_url(
        ClientMethod='get_object',
        Params={
            'Bucket': bucket,
            'Key': key
        },
        ExpiresIn=ttl,
    )

def detect_faces_or_text(bucket, key, collection_id=FACE_COLLECTON, threshold=FACE_THRESHOLD, table_name=FACE_DDB_TABLE):
    # Get timestamp from key
    timestamp = float(key.split('_')[2].split('/')[1])
    # NOTE: this will return an error if it doesn't find any faces in an image
    start_inference=time.time()
    response = rekognition.search_faces_by_image(
        Image={
            "S3Object": {
            "Bucket": bucket,
            "Name": key,
            }
        },
        CollectionId=collection_id,
        FaceMatchThreshold=threshold,
        MaxFaces=1,
    )
    print('rekognition for {}/{} latency: {}'.format(bucket, key, time.time()-start_inference))
    #print('search face by image', collection_id, threshold, response)
    table = dynamodb.Table(table_name)
    faces = []
    words = []
    for match in response['FaceMatches']:
        start_ddb = time.time()
        face = table.get_item(Key={'RekognitionId': match['Face']['FaceId']})
        print('ddb lookup for {} latency: {}'.format(match['Face']['FaceId'], time.time()-start_ddb))
        if 'Item' in face:
            push_to_cloudwatch('Face', round(match['Face']['Confidence'], 2), timestamp)
            faces.append({
                'RekognitionId': match['Face']['FaceId'],
                'Confidence': match['Face']['Confidence'],
                'Name': face['Item']['FullName'],
                'Url': get_signed_url(face['Item']['Bucket'], face['Item']['Key']),
            })
    # # If we didn't find any known faces, attempt to return words (Name & username)
    # # TODO: consider reading the meta-data, and only doing this if image is large
    # if len(faces) == 0:
    #     response = rekognition.detect_text(
    #         Image={
    #             "S3Object": {
    #                 "Bucket": bucket,
    #                 "Name": key,
    #             }
    #         },
    #     )
    #     for r in response['TextDetections']:
    #         if r['Type'] == 'WORD':
    #             push_to_cloudwatch('Word', round(r['Confidence'], 2), timestamp)
    #             words.append(r['DetectedText'])
    return {
        'Url': get_signed_url(bucket, key),
        'Faces': faces,
        #'Words': words
    }

def publish_message(payload, topic_arn=FACE_TOPIC_ARN):
    subject = '{}-{}'.format(payload["ThingName"], int(time.time()))
    msg = json.dumps({"default": json.dumps({ "DeepLens": payload }) })
    response = sns.publish(
        TopicArn=topic_arn,
        Subject=subject,
        MessageStructure='json',
        Message=msg,
    )
    return response['MessageId']

def lambda_handler(event, context):
    '''Demonstrates S3 trigger that uses
    Rekognition APIs to detect faces, labels and index faces in S3 Object.
    '''
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.unquote_plus(event['Records'][0]['s3']['object']['key'].encode('utf8'))
    try:
        payload = detect_faces_or_text(bucket, key)
        print('detect faces: {}'.format(json.dumps(payload)))
        if payload['Faces']:
            ret = s3.head_object(Bucket=bucket,Key=key)
            payload["ThingName"] = ret['Metadata']['thingname']
            message_id = publish_message(payload)
            print('publish sns messageId: {}'.format(message_id))
        return payload
    except Exception as ex:
        print("Error processing object {} from bucket {}: {}".format(key, bucket, ex))
        raise ex
