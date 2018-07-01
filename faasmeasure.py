import boto3
import json
import threading
import random
import os
import sys

numpar = 3
simulate = True

# FIXME
full = True
ccost = 0

def process():
    global ccost, full

    if simulate:
        response = {"cost": 5.0, "remaining": random.randrange(9)}
    else:
        fullresponse = lambdainvocation.invoke(FunctionName="proxycollectiveshipment", Payload="{}")
        response = json.loads(fullresponse["Payload"].read().decode("utf-8"))
    ccost += response["cost"]
    print("{:4d} remaining, cumulative cost {:.8} USD".format(response["remaining"], ccost))
    if response["remaining"] <= 0:
        full = False

def measure():
    while full:
        lambdainvocation = boto3.client("lambda")
        threads = []
        for i in range(numpar):
            if numpar == 1:
                process()
            else:
                t = threading.Thread(target=process)
                threads.append(t)
                t.start()
            if not full:
                break
        for t in threads:
            t.join()

if __name__ == "__main__":
    f = open("data/faasmeasure.{}.{}.log".format(numpar, simulate), "w")
    sys.stdout = f
    measure()
    f.close()
