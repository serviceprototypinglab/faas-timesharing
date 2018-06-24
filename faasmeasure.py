# run: python3 -u faasmeasure.py | tee faasmeasure.log

import boto3
import json

ccost = 0
while True:
    lambdainvocation = boto3.client("lambda")
    fullresponse = lambdainvocation.invoke(FunctionName="proxycollectiveshipment", Payload="{}")
    response = json.loads(fullresponse["Payload"].read().decode("utf-8"))
    ccost += response["cost"]
    print("{:4d} remaining, cumulative cost {:.8} USD".format(response["remaining"], ccost))
    if response["remaining"] <= 0:
        break
