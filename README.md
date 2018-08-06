# Virtual concierge

## Overivew

Virtual cocierge is an integrated solution that provide facial rekogition at the edge powered by Deep Lens and AI in the cloud to greet a user with a Summerian host.

## Lambda functions

### Deeplens Face detection

This lambda runs on the deeplens camera and is responsible for the inference that detects faces
in frame of a video stream. For each face it detects it pushed the croped face image to S3 for matching.

### Rekognition Detect faces

This lambda is triggered by a putObject event from the deeplens face detection lambda and calls
[AWS Rekognition](https://aws.amazon.com/rekognition/) to get a list of faces looked up against dynamodb.

It will then raise an SNS with the topic that matches the IoT Topic, and includes Faces, or Words eg:

```
{
  "TopicUrl": "$aws/things/XXXXXXX/shadow/get",
  "Url": "https://s3.amazonaws.com/x/y.jpg",
  "Faces": [
    {
      "RekognitionId": "aaaa-bbbb-cccc",
      "Name": "First Last",
      "Confidence": 0.995
    }
  ]
}
```

### Rekognition Index faces

This lambda will index a face into Rekognition, and store the name pulled from metadata into dynamodb.

## Development and Testing

Setup your deeplens camera and create all the required IAM roles.  

Build and deploy the greengrass face detection template, and publish version 1.

We will then create following resources:
* 2 lambda functions (index & detect)
* 2 S3 bucket (index & faces)
* 1 DynamoDB table

Using [AWS Serverless Application Model, or SAM](https://github.com/awslabs/serverless-application-model) deploy the above resources.

### Build

To build the lambda source packages run the following command:

```
make package-rekognition profile=<your_aws_profile>
```

### Deployment

To deploy the lambda functions run the following command:

```
make deploy-rekognition profile=<your_aws_profile>
```
