from score import Scorer
import cv2
import numpy as np
import os

# Get the updated scorer
model_dir = '../models'
scorer = Scorer(model_dir)

# usernames = ['julbrigh', 'joshfo', 'sssalim', 'djenny']
# names = ['Julian Bright', 'Josh Fox', 'Stephen Salim', 'Jenny Davies']
# vecs = []
# for i, username in enumerate(usernames):
#     path = './people/{}.jpg'.format(username)
#     print(path)
#     img = cv2.imread(path)
#     vec = scorer.vectorize(img)
#     vecs.append(vec)

vecs = []
names = []
ingest_dir = '../../rekognition-ingest'
import csv
with open(os.path.join(ingest_dir, 'people.tsv'), 'rb') as f:
    reader = csv.reader(f, delimiter='\t')
    for row in reader:
        if True: #row[2].startswith('MEL') or row[2].startswith('SYD'):
            fn = os.path.join(ingest_dir, 'aligned/{}.jpg'.format(row[0]))
            img = cv2.imread(fn)
            vec = scorer.vectorize(img)
            names.append(row[1])
            vecs.append(vec)
            print(row[1])

vecs = np.array(vecs)

# Save back the model directory
np.savez(os.path.join(model_dir, 'people.npz'), names=names, vecs=vecs)
print('saved', vecs.shape)
