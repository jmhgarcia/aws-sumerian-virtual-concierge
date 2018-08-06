from score import Scorer
import cv2

# Get the updated scorer
model_dir = '../models'
scorer = Scorer(model_dir)
print(scorer.vecs.shape)

# get vectorized image
img = cv2.imread('../people/julbrigh_test.jpg')
bbox = [30,60,80,100]
vec = scorer.vectorize(img, bbox)
print(vec.shape, vec.tolist())

# get the similar records
sim, z_score, prob, name = scorer.similar(vec)
print(sim, z_score, prob, name)
