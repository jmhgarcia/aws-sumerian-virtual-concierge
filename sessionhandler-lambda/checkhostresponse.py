import json
import boto3
import os
import time

dynamodb = boto3.resource('dynamodb')

def get_session(rekid,tablename):
    ddbtable = dynamodb.Table(tablename)
    return ddbtable.get_item(Key={'RekognitionId': rekid})

def update_status(rekid,status,tablename):
    ddbtable = dynamodb.Table(tablename)
    return ddbtable.update_item(Key={'RekognitionId': rekid},UpdateExpression='SET HostResponse = :val1',ExpressionAttributeValues={':val1': status})

def lambda_handler(event, context):
    try:
        result = get_session(event['Faces'][0]['RekognitionId'],'virtual-concierge-session')
        if 'Item' in result:
            event['HostResponse'] = {}
            hostresp = str(result['Item']['HostResponse'])
            if hostresp == 'remindhost':
                event['HostResponse']['State'] = 'remindhost'
                update_status(event['Faces'][0]['RekognitionId'],'waiting','virtual-concierge-session')
            elif hostresp == 'in-progress' or hostresp == 'waiting':
                event['HostResponse']['State'] = 'waiting'
                update_status(event['Faces'][0]['RekognitionId'],'waiting','virtual-concierge-session')
            elif hostresp == 'comingout' or hostresp == 'comingoutsoon':
                event['HostResponse']['State'] = result['Item']['HostResponse']
                update_status(event['Faces'][0]['RekognitionId'],'waiting','virtual-concierge-session')
            elif hostresp == 'hostdetected':
                event['HostResponse']['State'] = result['Item']['HostResponse']
                hostface = result['Item']['HostFacePayload']
                
                xhostface = json.loads(hostface)
                host = xhostface[0]
                event['Faces'][0] = host
                event['UserDetail']['Name'] = host['Name']
                event['UserDetail']['PhotoUrl'] = host['Url']
                
                waittime = int(round(time.time() * 1000)) - int(result['Item']['CreatedAt'])
                x = (waittime / 1000) / 60
                event['TotaWaitTime'] = round( x , 2)
                event['Complete'] = True
            else:
                event['HostResponse']['State'] = 'waiting'
        else:
            event['HostResponse']['State'] = 'waiting'
            
        return(event)  # Echo back the first key value
    except Exception as e:
        print(e)
        print('Error Checking HostResponse Status')
        raise e