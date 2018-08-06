
from __future__ import print_function

import boto3
import json
import logging
import os
import base64

from urllib2 import Request, urlopen, URLError, HTTPError

#configuration
SLACK_CHANNEL = "#general"
HOOK_URL = os.environ['SlackWebHook']
# Setting up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def generate_params(state,event):
    rekogid = "&rekogid=" + event['Faces'][0]['RekognitionId']
    state = "&state=" + state
    response = rekogid + state   
    return response
    
def lambda_handler(event, context):
    
    thingname = event['ThingName']
    if event['FaceDetection']['FaceStatus'] == "screen-face-unknown":
        name="unknown"
        photo="unknown"
        hslackid="@everyone"
    else:        
        name=event['Faces'][0]['Name']
        photo=event['Faces'][0]['Url']
        hslackid=event['AppointmentDetection']['HostSlackId']
    
    comingout_response = os.environ['RespionseUrl'] + "?"+ generate_params('comingout',event)
    comingoutsoon_response = os.environ['RespionseUrl'] + "?" + generate_params('comingoutsoon',event)
    
    print(comingout_response)
    
    slack_message =  {
                    'channel': SLACK_CHANNEL,
                    "text": "<"+hslackid+"> You have a Guest ! Please come out and greet.",
                    "attachments": [{
                        "color": "#2eb886",
                        "author_name": "ReceptionistBot",
                        "thumb_url": photo,
                        "fields": [{
                            "title": "Name",
                            "value": name,
                            "short": True
                        }],
                        "actions": [{
                            "type": "button",
                            "text": "Coming out now",
                            "url": comingout_response ,
                            "style": "primary"
                        }, {
                            "type": "button",
                            "text": "Couple of mins",
                            "url": comingoutsoon_response,
                            "style": "danger"
                        }]
                    }]
                }
    
    #slack_message = json.dumps(message)
    logger.info(str(slack_message))
    
    req = Request(HOOK_URL, json.dumps(slack_message))
    try:
        response = urlopen(req)
        response.read()
        logger.info("Message posted to %s", slack_message['channel'])
    except HTTPError as e:
        logger.error("Request failed: %d %s", e.code, e.reason)
    except URLError as e:
        logger.error("Server connection failed: %s", e.reason)

    return(event)