import boto3
import base64
import time
#import scipy.ndimage

def emulate_scipy(img):
    s = len(img) / 100000
    print("sleep {}s".format(s))
    time.sleep(s)

def lambda_handler(event, context):
    tstart = context.get_remaining_time_in_millis()
    sqs = boto3.resource("sqs")
    queue = sqs.get_queue_by_name(QueueName="bagoftasks")
    number = 0
    while True:
        msgs = queue.receive_messages(MaxNumberOfMessages=1)
        if not msgs:
            break
        emulate_scipy(msgs[0].body)
        msgs[0].delete()
        number += 1
        t = context.get_remaining_time_in_millis()
        tx = 100 - int(100 * (t / 100 - int(t / 100)))
        print("{}ms remaining {}ms used".format(t, tx))
        if tx > 80:
            print("good ratio, giving up this instance")
            print("total time used: {} of {}".format(tstart - t, tstart))
            return number
