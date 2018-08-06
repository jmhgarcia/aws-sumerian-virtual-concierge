frame_region := "ap-southeast-2"
profile ?= rekognition

# creating the collection needs to be done with CLI at the moment

create-rekognition:
	aws rekognition create-collection --collection-id virtual-concierge \
	--profile $(profile) --region $(frame_region)

setup: create-rekognition

package-deeplens:
	#aws s3 mb s3://virtual-concierge-deployment-greengrass --profile $(profile) --region us-east-1
	aws cloudformation package \
	--template-file deeplens-face-detection.yaml \
	--output-template-file deeplens-face-detection-output.yaml \
	--s3-bucket virtual-concierge-deployment-greengrass --profile $(profile) --region us-east-1

deploy-deeplens:
	aws cloudformation deploy \
  --template-file deeplens-face-detection-output.yaml \
  --stack-name virtual-concierge-deeplens-stack --profile $(profile) --region us-east-1

deeplens: package-deeplens deploy-deeplens

package-rekognition:
	#aws s3 mb s3://virtual-concierge-deployment-rekognition --profile $(profile) --region ap-southeast-2
	aws cloudformation package \
	--template-file rekognition-lambda.yaml \
	--output-template-file rekognition-lambda-output.yaml \
	--s3-bucket virtual-concierge-deployment-rekognition --profile $(profile) --region ap-southeast-2

deploy-rekognition:
		aws cloudformation deploy \
	  --template-file rekognition-lambda-output.yaml \
	  --stack-name virtual-concierge-rekognition-stack --profile $(profile) --region ap-southeast-2 \
	  --capabilities CAPABILITY_NAMED_IAM

rekognition: package-rekognition deploy-rekognition

# todo: create a lambda version, and then a deep lens project pointing to this version
# https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lambda-version.html
