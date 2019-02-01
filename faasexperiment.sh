mkdir -p data
rm -f data/*.log

for i in `seq 1 20`
do
	python3 -u faasproducer.py _testdata.ds2-small/ 2>&1 | tee -a data/experiment.log
	python3 -u faasmeasure.py $i False 0 2>&1 | tee -a data/experiment.log
done
