# mydropbox-fun

##CMPE 281: Cloud Project-1 MyDropBox

#####University Name: http://www.sjsu.edu/
#####Course: Cloud Technologies
#####Professor: Sanjay Garje
#####ISA: Anushri Srinath Aithal
#####Student: Poorva Agarwal
####Project Introduction
Mydropbox application is the integrated solution for users to allow secure file access and storage from anywhere, with any device. Users can create an account, sign in, upload new files, update existing ones, delete and download them. 

###Features of the application
1. Register an Account

2. Sign into the application

3. Upload a file

4. List of all files

5. Download files

6. Update File

7. Delete Files

###Architecture Diagram

###PreRequisites
AWS Components to be set up-

**EC2**: The EC2 instance will be created and the build file of the project will be deployed in the web apps folder of the APache server. Further, AMI of this instance will be created which will be used in the launch configuration of the AutoScaling group.
**S3**: This will be used to store the user's uploaded files. A base bucket will be created and inside it the files will be uploaded against each user. The storage of this bucket will be Standard S3.
**S3-Infrequent Access:** Another bucket will be created in different region whose stores will be S3-IA.
**S3-Transfer Acceleration**: This will be enabled on the buckets for faster upload of files.
**Amazon Glacier:** As per the Lifecycle policy, the files will be archived in this.
**RDS:** A MySQl instance will be created in this, where data related to user and corresponding files uploaded will be saved.
**CloudFront:** This has been configured for download of files from s3.
**Classic Load Balancer:** This has been configured to distribute the load between the EC2 instances created.
**AutoScaling Group: **This has been configured to auto scale the EC2 instance for higher availability and scalability.
**Route 53: **The IP address of the application will be resolved by this Domain Name Server.
**CloudWatch:** To set up monitoring on the S3 bucket.
**Lambda:** On the delete of any file from S3, it invoked the Lambda function (created in python) which further invoked SNS Topic to send notification emails.
**SNS:** Configured to send email to subscribers of the topic created in it.
Setup Jenkins to run build after each commit from Github.
Set AWS Code Deploy Application to automate the build deploy to EC2 instance.


###Configuration on Local Machine

**Softwares required to be setup : **Python, Flask, Boto3, Apache2, MYSQL Workbench

**Run project locally**

Download the code from this repository.
Set Up database
**Backend Setup:**
- Make sure python, pip, mysql are installed. Create and activate a virtual environment inside the “server” directory.
- Installed the required packages using requirement.txt file.
- Start the python application using python app.py
- Make sure server is up and running at port 5000

**Front End Setup:**
- Navigate to the front end project.
- Install the required dependencies from package.json file using npm install command.
- Start the front end application in dev environment using npm run dev.
- Application will start on port 8080 default.
- AWS setup:
- Create a bucket on S3.
- Create an IAM user in the AWS console and assign it the administrator access.
- Generate an access key for this user and keep a note of the access id and secret key.
- Update the user's access id, secret key, cloudfront url, cloudfront id, basebucket name, replication bucket name.
- The application will be accessed at http://localhost:8080.
- Once it runs fine here, it can be deployed to the EC2 instance using AWS code Deploy.
