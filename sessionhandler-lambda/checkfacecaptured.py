import json

def lambda_handler(event, context):
    try:
        print(json.dumps(event))
        if 'Faces' in event:
            x = event['Faces']
            if len(x) == 0:
                event['FaceDetection'] = {}
                event['FaceDetection']['FaceStatus'] = "screen-face-unknown"
                return(event)  
            else:
                event['FaceDetection'] = {}
                event['FaceDetection']['FaceStatus'] = "screen-face-known"
                return(event)  
        else:
            event['FaceDetection'] = {}
            event['FaceDetection']['FaceStatus'] = "screen-face-unknown"
            return(event)   
    except Exception as e:
        print(e)
        print("Error Finding Face")
        raise e
    