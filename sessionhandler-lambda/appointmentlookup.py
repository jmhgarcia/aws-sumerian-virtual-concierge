import json
import boto3
dynamodb = boto3.resource('dynamodb')

def find_scheduled_Appointment(event):
    # This is the function where we search for appointment.. at the moment this is just mocked.
    # Ideally this should query appointment table
    appointment = {}
    appointment['AppointmentFound'] = 'True'
    appointment['Host'] = '	Stephen Salim'
    appointment['RekogId'] = 'd92188d4-27cf-40c0-a871-2ce92b95cabe'
    appointment['HostSlackId'] = '@sssalim'
    
    update_appointment(event['Faces'][0]['RekognitionId'],appointment['RekogId'],'virtual-concierge-session')
    return(appointment)
    
def update_appointment(rekid,host,tablename):
    ddbtable = dynamodb.Table(tablename)
    return ddbtable.update_item(Key={'RekognitionId': rekid},UpdateExpression='SET AppointmentHost = :val1',ExpressionAttributeValues={':val1': host})

def lambda_handler(event, context):
    event['AppointmentDetection'] = {}
    event['AppointmentDetection'] = find_scheduled_Appointment(event)
    return(event)  # Echo back the first key value
