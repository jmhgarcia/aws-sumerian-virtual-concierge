# Create the virtual-concierge score api
docker build -t face-detection .

# Login and push image
`aws ecr get-login --profile rekognition --no-include-email --region ap-southeast-2`
docker tag face-detection:latest 882607831196.dkr.ecr.ap-southeast-2.amazonaws.com/virtual-concierge:latest
docker push 882607831196.dkr.ecr.ap-southeast-2.amazonaws.com/virtual-concierge:latest

# Set the envrionment variable from profile
AWS_ACCESS_KEY_ID=$(aws --profile rekognition configure get aws_access_key_id)
AWS_SECRET_ACCESS_KEY=$(aws --profile rekognition configure get aws_secret_access_key)

# Ryn the docker container
docker run -p 5000:5000 --rm \
   -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
   -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
   face-detection:latest
