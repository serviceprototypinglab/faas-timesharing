import scipy.ndimage
import glob
import time
import math
import statistics
import sys

def process(imagepath):
	image = scipy.ndimage.imread(imagepath)
	x_img = scipy.ndimage.median_filter(image, 2)

def schedule(testdatapath):
	f = open("strategies.csv", "w")
	print("#remtime-threshold(s),cumulativecost-mean(s),stddev,maxthread(s)", file=f)
	f.close()

	imagepaths = glob.glob("{}/*.jpg".format(testdatapath))

	print("{} data units; theoretic max savings boundary = {:.2f}s".format(len(imagepaths), len(imagepaths) * 0.5))

	for thresholdfactor in range(10):
		allccosts = []
		maxthread = 0
		for i in range(10+1):
			t1 = time.time()
			num = 0
			ccost = 0
			dt = 0
			for imagepath in imagepaths:
				process(imagepath)
				t2 = time.time()
				num += 1
				dt = 10 * (t2 - t1) # duration x100ms
				lt = 1 - (dt - int(dt)) # losstime
				#print(lt)
				if lt < thresholdfactor / 10:
					pass
				else:
					cost = math.ceil(dt)
					ccost += cost
					print("cost", cost, "for", num, "cumulative", ccost)
					t1 = t2
					dt = 0
					num = 0
					if cost > maxthread:
						maxthread = cost
			if dt > 0.0001:
				cost = math.ceil(dt)
				ccost += cost
				print("cost", cost, "for", num, "cumulative", ccost, "leftover")
				if cost > maxthread:
					maxthread = cost
			allccosts.append(ccost)
		print("all-cumulative avg", statistics.mean(allccosts), "stddev", statistics.stdev(allccosts))
		f = open("strategies.csv", "a")
		print("{:.2f},{:.2f},{:.2f},{}".format(thresholdfactor / 10, statistics.mean(allccosts), statistics.stdev(allccosts), maxthread), file=f)
		f.close()

if __name__ == "__main__":
	if len(sys.argv) != 2:
		print("Syntax: {} <dsdir>".format(sys.argv[0]), file=sys.stderr)
		sys.exit(1)
	schedule(sys.argv[1])
