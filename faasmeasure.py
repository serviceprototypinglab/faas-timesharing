import boto3
import json
import threading
import random
import os
import sys

# These two are configurable via the CLI
numpar = 1
simulate = False

# FIXME: global variables
full = True
ccost = 0

def process(lambdainvocation):
    global ccost, full

    if simulate:
        response = {"cost": 5.0, "remaining": random.randrange(9)}
    else:
        # this is faasproxy.py, which in turn invokes the 'queueeater' function, i.e. faasconsumer.py
        fullresponse = lambdainvocation.invoke(FunctionName="proxycollectiveshipment", Payload="{}")
        response = json.loads(fullresponse["Payload"].read().decode("utf-8"))
    ccost += response["cost"]
    print("{:4d} remaining, cumulative cost {:.8} USD".format(response["remaining"], ccost))
    if response["remaining"] <= 0:
        full = False

def measure():
    while full:
        threads = []
        for i in range(numpar):
            lambdainvocation = boto3.client("lambda")
            if numpar == 1:
                process(lambdainvocation)
            else:
                t = threading.Thread(target=process, args=(lambdainvocation,))
                threads.append(t)
                t.start()
            if not full:
                break
        for t in threads:
            t.join()

if __name__ == "__main__":
    if len(sys.argv) == 3:
        numpar = int(sys.argv[1])
        if sys.argv[2] == "True":
            simulate = True
    else:
        print("Syntax: {} <numpar> <simulate:True/False>".format(sys.argv[0]), file=sys.stderr)
        sys.exit(-1)
    os.makedirs("data", exist_ok=True)
    f = open("data/faasmeasure.{}.{}.log".format(numpar, simulate), "w")
    sys.stdout = f
    measure()
    f.close()
