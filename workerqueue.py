import boto3
import random

QN = "bagoftasks"

sqs = boto3.resource("sqs")
try:
	queue = sqs.get_queue_by_name(QueueName=QN)
except:
	queue = sqs.create_queue(QueueName=QN, Attributes={"DelaySeconds": "0"})

msgbody = "test" + str(random.randrange(10000))

print("send", msgbody)

response = queue.send_message(MessageBody=msgbody)

msgs = queue.receive_messages(MaxNumberOfMessages=1)

print("receive", msgs[0].body)

msgs[0].delete()
