## Sample Lambda Layers Application

This is a sample AWS Serverless Application Model (SAM) Application that scrapes the [AWS Technical Evangelists](https://aws.amazon.com/developer/community/evangelists/) site for headshots, and passes them to AWS Rekognition to detect faces and gather some attirbutes about the faces (Gender, MinAge, MaxAge).

It contains a single Lambda Function that uses Beautiful Soup (BS4) and the LXML Parser to scrape the web page for `<img>` tags and then downloads the images to send to AWS Rekognition. 

The Lambda function depends on both bs4 and lxml, however neither are included within the function code, we provde them via a Lambda Layer to demonstrate its functionality.

- **bs4-layer** - Includes the Beautiful Soup Python Library and the LXML library. LXML is a platform-specific library so historically you would have had to build this on Amazon Linux for all of your Lambda functions. By creating a layer for LXML we only have to build it once, and then we can re-attach the layer to multiple functions.

## Deploying your Application

You can use SAM to deploy the layers along with the function, or if you are using this for demonstration purposes or would like to understand a little more about layers, you could deploy this manually. The steps for both are provided below.

### Using SAM

#### Getting Started

Firstly you will need the SAM-CLI installed and configured on your local machine. You will also need an upto date version of the AWS CLI. Versions are in ***requirements-dev.txt***

Run the following command to make sure you have the minimum required versions installed.

`pip install -r requirements-dev.txt`


More instructions on installing sam-cli are [here](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html).

To check that the SAM-CLI is running run
`sam --version`

Next make sure that you are in the root directory that this repository has been cloned to.

#### Packaging your Application with SAM

To package your application, create an Amazon S3 bucket that the package command will use to upload your ZIP deployment package. You can use the following command to create the Amazon S3 bucket:

`aws s3 mb s3://bucket-name --region <region-name>`

Package the application using the SAM CLI

    sam package \
    	--template-file template.yaml \
    	--output-template-file serverless-output.yaml \
    	--s3-bucket <bucket-name>

The package command returns an AWS SAM template named serverless-output.yaml that contains the CodeUri that points to the deployment zip in the Amazon S3 bucket that you specified. This template represents your serverless application. You are now ready to deploy it.

#### Deploying your Application with SAM

You can deploy your application using the `sam deploy` command as shown below. This takes the output template from the above package command and deploys it using AWS Cloudformation.

    sam deploy \
        --template-file serverless-output.yaml \
        --stack-name new-stack-name \
        --capabilities CAPABILITY_IAM


### Manual Deployment via AWS Console

#### Manually creating Layers
To build a Lambda Layer you need to upload a .zip file with the contents of the layer compressed. Unlike a function, a Layer does not require a handler, so it can include just libraries for example. That is what we will be doing in this sample app.

***NOTE: One trick to packaging a Lambda Layer for Python is that the contents of the layer must sit within a folder with one of the following names. You should not place the contents of the layer into the root of the .zip file.***

**Acceptable folder names for Python are: python, python/lib/python3.7/site-packages**

More info on including library dependencies in a layer [here](https://docs.aws.amazon.com/lambda/latest/dg/configuration-layers.html#configuration-layers-path)

In the **layers** directory you will see a sub folder, *bs4-layer* This folder will include a subfolder named **python** where the libraries have been installed.

In the parent layer folder, there is also a .zip file that is the both the **python** folder and its contents compressed. This is the file we will need to manually create the layer in the AWS Console.

This README will not provide step-by-step guide on how to use the AWS console to achieve this, but now you know which .zip file you need to manually create the layers this should be reasonably straight forward in the console. 

#### Manually Deploying Lambda Function

The Lambda function sits in the **functions/get-evangelists/lambda_function.py** file. You can copy this code and paste it directly into the AWS Lambda Console editor when you create a function. This function does not require any triggers, but it will require an IAM Role that has permissions to **detectFaces** on the AWS Rekognition service, as well as the usual permissions for writing logs to CloudWatch Logs.

The Function code is not the most optimal and takes ~12secs to run, so make sure that your function has a sufficient timeout (I specified 30seconds in the SAM template).

Finally, In the Lambda Console for your function, select the Layers icon underneath your function and add the layer that was previously created.

##Testing your Application

Once the Application is deployed, you can test by invoking the Lambda function directly. Either in the AWS Console or using the following CLI command:

`aws lambda invoke --function-name <function-name> --log-type Tail output.txt`

If you do not know the function name, then you can use the following command to get a list of functions in your account:

`aws lambda list-functions`

The function does not require any payload or event, so we can leave that parameter for now. If testing in the AWS Console, you may need to create a test-event. You can create any event, the function will ignore it.

The function will output "Sucessfully Completed" into the output.txt file if it is successful. In this basic example, data from AWS Rekognition is only written to the logs. You can view the logs in the AWS CloudWatch Logs Console or from within the Functions Console if testing there.

If using the cli to invoke the function, by specifying the *--log-type* parameter, the command also requests the tail end of the log produced by the function. The log data in the response is base64-encoded. Use the base64 program to decode the log.

    echo "base_64_encoded_log_output"| base64 --decode
    START RequestId: 8b6d71bc-f8d8-11e8-bf82-c5d532d4aaf8 Version: $LATEST
    Page Title:  <title>Technical Evangelists | Community Learning | AWS Developer Center</title>
    -------
    Jeff is a Male who is between 45 and 65
    -------
    Julio is a Male who is between 20 and 38
    ....



