import boto3
import cv2
import os
import numpy as np
import time
from score import Scorer
from flask import Flask, request, jsonify

s3 = boto3.resource('s3', region_name=os.getenv('REGION_NAME', 'ap-southeast-2'))
deeplens_bucket = os.getenv('DEEPLENS_BUCKET', 'deeplens-virtual-concierge-model')
model_dir = os.getenv('MODEL_DIR', '/tmp')

# Load model
scorer = None

def downlad_model(model_dir):
    print('downloading mobilenet model')
    download_start = time.time()
    bucket = s3.Bucket(deeplens_bucket)
    files = ['mobilenet1-0000.params','mobilenet1-symbol.json','people.npz']
    for file in files:
        dest = os.path.join(model_dir, file)
        key = os.path.join('mobilenet1', file)
        print('downloading {} to {}'.format(key, dest))
        bucket.download_file(key, dest)
    print('Loaded {} files in {}s'.format(len(files), time.time()-download_start))

def load_model(model_dir):
    global scorer
    print('loading mobilenet model')
    model_start = time.time()
    scorer = Scorer(model_dir)
    print('Loaded mobilenet model {} in {}s'.format(scorer.vecs.shape, time.time()-model_start))

# Lambda like function handler
def function_handler(event, context):
    if 'bucket' in event and 'key' in event:
        score_start = time.time()
        image_object = s3.Object(event['bucket'], event['key'])
        data = np.frombuffer(image_object.get()['Body'].read(), np.uint8)
        img = cv2.imdecode(data, -1)
        vec = scorer.vectorize(img)
        print('Download and score {}/{} in {}s'.format(event['bucket'], event['key'], time.time()-score_start))
        return {
            "bucket": event['bucket'],
            "key": event['key'],
            "vector": vec.tolist()
        }

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello score API!"

'''
# Post to this endpoint with
curl -X POST -v -H "Content-Type: application/json" \
    -d '{ "bucket": "virtual-concierge-frames-ap-southeast-2", "key": "faces/7_26/20_50/1532652558_0.jpg" }' \
    http://127.0.0.1:5000/classify
'''
@app.route('/classify', methods = ['POST'])
def classify():
    return jsonify(function_handler(request.get_json(), None))

@app.route('/update', methods = ['POST'])
def update():
    downlad_model(model_dir)
    load_model(model_dir)
    return jsonify({ 'ok': True, 'size': scorer.vecs.shape[0] })

if __name__ == '__main__':
    downlad_model(model_dir)
    load_model(model_dir)
    app.run(host='0.0.0.0')
