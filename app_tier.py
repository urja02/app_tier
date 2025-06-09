import boto3
from model.face_recognition import face_match
from dotenv import load_dotenv
import os
import time 
import json
# Loading the environment variables from the .env file
load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')  # Default to us-east-1 if not specified

client = boto3.client(
    'sqs',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)
s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

# 1. Implement the polling logic to get the image name from the queue. Polling logic should continuously check if 
# if there is a message in the queue, and if not, sleep for 5 seconds and check again.
# 2. Implement this code as an infinite loop to ensure that the process does not stop after one request.
def run():
    while True:
        request_msg = client.receive_message(
            QueueUrl='https://sqs.us-east-1.amazonaws.com/523955944173/34294310-req-queue',
            VisibilityTimeout=10,
            WaitTimeSeconds=10)
        if request_msg == None:
            time.sleep(5)
            continue
        elif request_msg.get('Messages', None) == None:
            time.sleep(5)
            continue
        else:
            break
   
    print("message received")
    body = json.loads(request_msg['Messages'][0]['Body'])
    img_name = body["file_name"]
    img_uuid = body['uuid']
    img_path = 'images/' + img_name
    s3_client.download_file('34294310-in-bucket', img_name, img_path)
    

    if os.path.exists(img_path):
        print("image found ", img_path)
        try:
            result = face_match(img_path)
            print("The result is ", result[0])
        except Exception as e:
            print("Error in face matching", e)
            return 
    else:
        print("Image not found", img_path)
        return 

    res_path = 'ml_result/'
    img_res = img_name.split('.')[0]
    with open(res_path+img_res,'w') as file:
        file.write(result[0])
    
    payload = {'uuid' : img_uuid, 'result' : result[0]}
    resp_msg = client.send_message(
        QueueUrl='https://sqs.us-east-1.amazonaws.com/523955944173/34294310-resp-queue',
        MessageBody=json.dumps(payload))
    print("message sent to the response queue")
    delete_msg = request_msg['Messages'][0]['ReceiptHandle']
    del_response = client.delete_message(
        QueueUrl='https://sqs.us-east-1.amazonaws.com/523955944173/34294310-req-queue',
        ReceiptHandle= delete_msg
    )
    print("message deleted from the request queue")

    with open(res_path+img_res, "rb") as f:
        s3_client.upload_fileobj(f, "34294310-out-bucket", img_res)
    print("result uploaded to the output bucket")
    os.remove(img_path)
    os.remove(res_path+img_res)
    print("image removed from the local directory")
    print("the process is complete")
    print("--------------------------------") 

if __name__ == "__main__":
    while True:
        run()


    # app tier reads messages from the queue, runs ml algo writes to a separeate queue. The result is also stored in the S3 bucket to validate late.
    # the web tier pushes the image to the S3 bucket as and when it gets it and it sends the name of the image to the queue.

    # the app tier pulls the queue and gets the image from the S3 bucket and runs the ML algo. Further saving the result in another S3 bucket.
    # each message in the queue has a size limit but you can never tell what image you get from the user.
    #request queue: producer -> 
#write  a script 
#upload image to S3 buvckrt and put request in request queue.