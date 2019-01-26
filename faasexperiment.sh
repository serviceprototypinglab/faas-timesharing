mkdir -p data
rm -f data/*.log

for i in `seq 1 20`
do
	python3 faasproducer.py _testdata.ds2-small/ 2>&1 | tee -a data/experiment.log
	python3 faasmeasure.py $i False 2>&1 | tee -a data/experiment.log
done
