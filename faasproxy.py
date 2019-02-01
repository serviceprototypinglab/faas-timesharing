import boto3
import time
import json

# assumption: proxy 128 MB, queueeater 4(memdiff)*128 MB = 512 MB
# aws lambda add-permission --function-name 'queueeater' --statement-id queueeater_reverse --action lambda:InvokeFunction --principal arn:aws:iam::*:role/lambda_basic_execution_sqs

def lambda_handler(event, context):
    tstart = context.get_remaining_time_in_millis()
    sqs = boto3.resource("sqs")
    queue = sqs.get_queue_by_name(QueueName="bagoftasks")
    sqs2 = boto3.client("sqs")
    a = sqs2.get_queue_attributes(QueueUrl=queue.url, AttributeNames=["ApproximateNumberOfMessages"])
    n = int(a["Attributes"]["ApproximateNumberOfMessages"])

    if event["bulk"]:
        threshold = 10
        if n < threshold:
            time.sleep((threshold - n) * 2)
            print("invocation after {}*2s delay due to {} tasks".format(threshold - n, n))
        else:
            print("direct invocation due to {} tasks".format(n))

    lambdainvocation = boto3.client("lambda")
    fullresponse = lambdainvocation.invoke(FunctionName="queueeater", Payload=json.dumps(event))
    response = json.loads(fullresponse["Payload"].read().decode("utf-8"))
    t = context.get_remaining_time_in_millis()
    response["proxyduration"] = 100 * (int((tstart - t) / 100) + 1)
    basepriceexec = 0.000000208
    basepriceinvc = 0.0000002
    memdiff = 4
    if event["baseline"] == "none":
        response["cost"] = ((response["duration"] * memdiff + response["proxyduration"]) / 100) * basepriceexec + 2 * basepriceinvc
    else:
        response["cost"] = response["duration"] / 100 * basepriceexec + basepriceinvc
    response["remaining"] = n - response["number"]
    return response
