import json
import boto3
import os
import uuid

sqs_client = boto3.client('sqs',region_name=os.environ['sdkregion'])
sqs_queue = os.environ['QueueUrl']


def get_name(name,mode):
    firstlastname = name.split(" ")
    if mode == 'first':
        result = firstlastname[0]
    if mode == 'last': 
        result = firstlastname[1]
    return result

def lambda_handler(event, context):
    try:
            event['SumerianHost'] = {}
            
            if 'HostResponse' in event:
                if event['HostResponse']['State'] == 'remindhost':
                    event['SumerianHost']['MsgType'] = 'assureguest'
                    event['SumerianHost']['Message'] = "Hi " + get_name(event['Faces'][0]['Name'],'first') + ", unfortunately your host has not responded yet. Let me send a reminder."
                    payload = event
                    thingname = event['ThingName']
                    sqs_client.send_message( QueueUrl=sqs_queue ,MessageBody=json.dumps(payload), MessageGroupId=thingname , MessageDeduplicationId= str(uuid.uuid4()))
                    return(event)
                
                if event['HostResponse']['State'] == 'comingout':
                    event['SumerianHost']['MsgType'] = 'comingout'
                    event['SumerianHost']['Message'] = get_name(event['Faces'][0]['Name'],'first') + "! your host is coming out to get you now."
                    payload = event
                    thingname = event['ThingName']
                    sqs_client.send_message( QueueUrl=sqs_queue ,MessageBody=json.dumps(payload), MessageGroupId=thingname , MessageDeduplicationId= str(uuid.uuid4()))
                    return(event)
                    
                if event['HostResponse']['State'] == 'comingoutsoon':
                    event['SumerianHost']['MsgType'] = 'comingoutsoon'
                    event['SumerianHost']['Message'] = get_name(event['Faces'][0]['Name'],'first') + "! your host is coming out to get you in a couple of minutes."
                    payload = event
                    thingname = event['ThingName']
                    sqs_client.send_message( QueueUrl=sqs_queue ,MessageBody=json.dumps(payload), MessageGroupId=thingname , MessageDeduplicationId= str(uuid.uuid4()))
                    return(event)

                if event['HostResponse']['State'] == 'hostdetected':
                    event['SumerianHost']['MsgType'] = 'notify'
                    event['SumerianHost']['Message'] = "Hi" + get_name(event['AppointmentDetection']['Host'],'first')  + " ! Good to see you have finally come out. Your guest has been waiting for " + str(event['TotaWaitTime']) + " minutes !"
                    payload = event
                    thingname = event['ThingName']
                    sqs_client.send_message( QueueUrl=sqs_queue ,MessageBody=json.dumps(payload), MessageGroupId=thingname , MessageDeduplicationId= str(uuid.uuid4()))
                    return(event)
                    
            else:
                if 'AppointmentDetection' in event:
                    if 'AppointmentFound' in event['AppointmentDetection']:
                        if event['AppointmentDetection']['AppointmentFound'] == 'True' :
                            host = event['AppointmentDetection']['Host']
                            event['SumerianHost']['MsgType'] = 'notify'
                            event['SumerianHost']['Message'] = "Alright, I have found your appointment with  <mark name='gesture:generic_c'/> " + host + ". <mark name='gesture:generic_a'/> Please take a seat, while I notify your arrival."
                            payload = event
                            thingname = event['ThingName']
                            sqs_client.send_message( QueueUrl=sqs_queue ,MessageBody=json.dumps(payload), MessageGroupId=thingname , MessageDeduplicationId= str(uuid.uuid4()))
                            return(event)
                            
                        if event['AppointmentDetection']['AppointmentFound'] == 'False' :
                            host = event['AppointmentDetection']['Host']
                            event['SumerianHost']['MsgType'] = 'reject'
                            event['SumerianHost']['Message'] = "Sorry,<mark name='gesture:defense'/> unfortunately you do not have an appointment with anyone, <mark name='gesture:generic_a'/> our visiting policy is by appointment only, please make a booking and come again."
                            payload = event
                            thingname = event['ThingName']
                            sqs_client.send_message( QueueUrl=sqs_queue ,MessageBody=json.dumps(payload), MessageGroupId=thingname , MessageDeduplicationId= str(uuid.uuid4()))
                            return(event)
                else:
                    if 'Faces' in event:
                        f = event['Faces']
                        event['UserDetail'] = {}
                        if len(f) > 0:
                            username = event['Faces'][0]['Name']
                            photourl = event['Faces'][0]['Url']
                            event['UserDetail']['Name'] = username
                            event['UserDetail']['PhotoUrl'] = photourl
                        else:
                            event['UserDetail']['Name'] = "Unknown"
                            event['UserDetail']['PhotoUrl'] = "Unknown"
                    
                    if 'FaceDetection' in event:
                        if 'FaceStatus' in event['FaceDetection']:
                            if event['FaceDetection']['FaceStatus'] == 'screen-face-known': 
                                event['SumerianHost']['MsgType'] = 'greeting'
                                event['SumerianHost']['Message'] = "Hello <mark name='gesture:wave'/> " +  get_name(username,'first') + " ! <mark name='gesture:big'/> Welcome to Tech Summit 2018, <mark name='gesture:generic_b'/> let me check if you have any appointment."
                                payload = event
                                thingname = event['ThingName']
                                sqs_client.send_message( QueueUrl=sqs_queue ,MessageBody=json.dumps(payload), MessageGroupId=thingname , MessageDeduplicationId= str(uuid.uuid4()))
                                return(event)
                                
                            if event['FaceDetection']['FaceStatus'] == 'screen-face-unknown' :
                                event['SumerianHost']['MsgType'] = 'checkagain'
                                event['SumerianHost']['Message'] = "Sorry,<mark name='gesture:defense'/> I cannot detect who <mark name='gesture:you'/> you are. <mark name='gesture:generic_b'/> let me send a message to the group to attend to you."
                                payload = event
                                thingname = event['ThingName']
                                sqs_client.send_message( QueueUrl=sqs_queue ,MessageBody=json.dumps(payload), MessageGroupId=thingname , MessageDeduplicationId= str(uuid.uuid4()))
                                return(event)
            return(event)
        
    except Exception as e:
        print(e)
        print("Error Sending Message to Sumerian")
        raise e