import boto3
import json
import threading
import random
import os
import sys
import time

# FIXME: global variables
full = True
ccost = 0
rem = 0

def process(lambdainvocation, numpar, simulate, threshold, baseline, bulk):
    global ccost, full, rem

    if simulate:
        response = {"cost": 5.0, "remaining": random.randrange(9)}
    else:
        # this is faasproxy.py, which in turn invokes the 'queueeater' function, i.e. faasconsumer.py
        pl = {"threshold": threshold, "baseline": baseline, "bulk": bulk}
        nsleep = 1
        ssleep = 0
        while True:
            try:
                fullresponse = lambdainvocation.invoke(FunctionName="proxycollectiveshipment", Payload=json.dumps(pl))
            except:
                time.sleep(nsleep)
                ssleep += nsleep
                nsleep *= 2
            else:
                break
        if ssleep > 0:
            print("warning: delayed invoke {} s due to network issues".format(ssleep))
        response = json.loads(fullresponse["Payload"].read().decode("utf-8"))
    if not "cost" in response:
        print("warning: invalid response received, setting cost/remaining to 0")
        response["cost"] = 0
        response["remaining"] = 0
    ccost += response["cost"]
    print("{:4d} remaining, cumulative cost {:.6f} USD".format(response["remaining"], ccost))
    if response["remaining"] <= 0:
        full = False
    if rem == 0 or response["remaining"] < rem:
        rem = response["remaining"]

def measure(f, numpar, simulate, threshold, baseline, bulk):
    crem = 0
    forig = sys.stdout
    sys.stdout = f
    t_start = time.time()
    while full:
        threads = []
        for i in range(numpar):
            lambdainvocation = boto3.client("lambda")
            if numpar == 1:
                process(lambdainvocation, numpar, simulate, threshold, baseline, bulk)
                threads.append(None)
            else:
                t = threading.Thread(target=process, args=(lambdainvocation, numpar, simulate, threshold, baseline, bulk))
                threads.append(t)
                t.start()
            if not full:
                break
        for t in threads:
            if t:
                t.join()
            if crem == 0 and rem > 0:
                crem = rem
            for i in range(crem - rem):
                print("+", end="", flush=True, file=forig)
            crem = rem
    print("", file=forig)
    t_end = time.time()
    print("overall processing time: {:.2f} s".format(t_end - t_start))
    print("configuration was: numpar={} simulate={} | threshold={} baseline={} bulk={}".format(numpar, simulate, threshold, baseline, bulk))
    sys.stdout = forig
    print("achieved {:.2f}s for numpar={} simulate={}".format(t_end - t_start, numpar, simulate))

if __name__ == "__main__":
    # Parameters configurable via the CLI
    numpar = 1
    simulate = False
    threshold = 90
    baseline = "none"
    bulk = False

    if len(sys.argv) >= 3:
        numpar = int(sys.argv[1])
        if sys.argv[2] == "true":
            simulate = True
        if len(sys.argv) >= 4:
            threshold = int(sys.argv[3])
        if len(sys.argv) >= 5:
            baseline = sys.argv[4]
        if len(sys.argv) >= 6:
            if sys.argv[5] == "true":
                bulk = True
    else:
        print("Syntax: {} <numpar:1> <simulate:false*/true> [<threshold:90(%)>] [baseline:none*/individual/all] [bulk:false*/true]".format(sys.argv[0]), file=sys.stderr)
        sys.exit(-1)
    os.makedirs("data", exist_ok=True)
    f = open("data/faasmeasure.{:02d}.{}.log".format(numpar, simulate), mode="w", buffering=1)
    measure(f, numpar, simulate, threshold, baseline, bulk)
    f.close()
