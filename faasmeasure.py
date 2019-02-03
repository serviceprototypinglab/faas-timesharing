import boto3
import json
import threading
import queue
import random
import os
import sys
import time

def process(lambdainvocation, numpar, simulate, threshold, baseline, bulk, q):
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

    cost = response["cost"]
    duration = response["duration"]
    rem = response["remaining"]
    full = True
    if rem <= 0:
        full = False

    print("{:4d} remaining, local duration {:.2f} s, local cost {:.6f} USD".format(rem, duration / 1000, cost))

    if q:
        q.put((cost, duration, full, rem))
    else:
        return (cost, duration, full, rem)

def measure(f, numpar, simulate, threshold, baseline, bulk):
    mrem = 0
    crem = 0
    cfull = True
    ccost = 0
    cduration = 0
    invocations = 0

    forig = sys.stdout
    sys.stdout = f

    q = None
    if numpar > 1:
        q = queue.Queue()

    t_start = time.time()
    while cfull:
        threads = []
        for i in range(numpar):
            lambdainvocation = boto3.client("lambda")
            if numpar == 1:
                cost, duration, full, rem = process(lambdainvocation, numpar, simulate, threshold, baseline, bulk, q)
                threads.append(None)
            else:
                t = threading.Thread(target=process, args=(lambdainvocation, numpar, simulate, threshold, baseline, bulk, q))
                threads.append(t)
                t.start()
            if not cfull:
                break
        for t in threads:
            if t:
                t.join()
                cost, duration, full, rem = q.get()
            invocations += 1
            ccost += cost
            cduration += duration
            if not full:
                cfull = False
            if crem == -1:
                continue
            if mrem == 0 or rem < mrem:
                mrem = rem
            if crem == 0 and rem > 0:
                crem = mrem
            for i in range(crem - mrem):
                print("+", end="", flush=True, file=forig)
            crem = mrem
            if crem == 0:
                crem = -1
    print("", file=forig)
    t_end = time.time()
    t_diff = t_end - t_start
    print("overall processing time: {:.2f} s, net duration: {:.2f} s, invocations {:2d}, cost: {:.6f} USD".format(t_diff, cduration / 1000, invocations, ccost))
    print("configuration was: numpar={} simulate={} | threshold={} baseline={} bulk={}".format(numpar, simulate, threshold, baseline, bulk))
    sys.stdout = forig
    print("spent {:.2f}s for experiment numpar={} simulate={}".format(t_diff, numpar, simulate))

    f = open("results.csv", "a")
    print("{:s},{:02d},{:02d},{:s},{:s},{:07.3f},{:02d},{:.6f}".format(str(simulate), numpar, threshold, baseline, str(bulk), cduration / 1000, invocations, ccost), file=f)
    f.close()

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
