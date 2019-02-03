import boto3
import base64
import glob
import sys
import time

def process_producer(imagepath, queue):
	bincontent = open(imagepath, "rb").read()
	hexcontent = base64.b64encode(bincontent).decode("utf-8")
	response = queue.send_message(MessageBody=hexcontent)

def schedule(testdatapath, queuename):
	imagepaths = glob.glob("{}/*.jpg".format(testdatapath))

	print("{} data units; theoretic max savings boundary = {:.2f}s".format(len(imagepaths), len(imagepaths) / 10 / 2))

	sqs = boto3.resource("sqs")
	try:
		queue = sqs.get_queue_by_name(QueueName=queuename)
	except:
		queue = sqs.create_queue(QueueName=queuename, Attributes={"DelaySeconds": "0"})

	msgs = queue.receive_messages(MaxNumberOfMessages=1)
	if msgs:
		print("queue not empty, results undefined, performing safe purge...")
		try:
			queue.purge()
		except:
			pass
		time.sleep(60)

	for imagepath in imagepaths:
		process_producer(imagepath, queue)
		print(".", end="", flush=True)
	print()

if __name__ == "__main__":
	QN = "bagoftasks"
	if len(sys.argv) != 2:
		print("Syntax: {} <dsdir>".format(sys.argv[0]), file=sys.stderr)
		sys.exit(1)
	schedule(sys.argv[1], QN)
