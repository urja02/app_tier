import os
import boto3
from dotenv import load_dotenv
import os
import time 
import json
import uuid
import random
# Loading the environment variables from the .env file
load_dotenv()
count = 5
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')

client = boto3.client(
    'sqs',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
   
)
s3_client = boto3.client('s3',aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,)

path = '../face_images_1000/'
i = 0 
files = os.listdir(path)
random.shuffle(files)
for file in files:
    with open(path+file, "rb") as f:
        random_uuid = str(uuid.uuid4())
        payload = {'uuid' : random_uuid, 'file_name' : random_uuid+file}

        s3_client.upload_fileobj(f, '34294310-in-bucket', random_uuid+file)
        client.send_message(
        QueueUrl='https://sqs.us-east-1.amazonaws.com/523955944173/34294310-req-queue',
        MessageBody=json.dumps(payload))
        print("message sent to the request queue")
        i += 1
        while True:
            response = client.receive_message(
                QueueUrl='https://sqs.us-east-1.amazonaws.com/523955944173/34294310-resp-queue',
                MaxNumberOfMessages=10,
                VisibilityTimeout=0,
                WaitTimeSeconds=10)
            flag = False
            if response == None:
                time.sleep(5)
                continue
            if response.get('Messages', None) == None:
                time.sleep(5)
                continue
            for msg in response['Messages']:
                body = json.loads(msg['Body'])
                if body['uuid'] == random_uuid:
                    flag = True
                    print("message received from the response queue", body['result'])
                    del_response = client.delete_message(
                        QueueUrl='https://sqs.us-east-1.amazonaws.com/523955944173/34294310-resp-queue',
                        ReceiptHandle= msg['ReceiptHandle'])
                    print("message deleted from the response queue")
                    break
            if flag:
                    break
         
        if i == count:
            break
        print("img uploaded to the output bucket")


    


    