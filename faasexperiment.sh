rm -rf data-experiment/
mkdir -p data-experiment
rm results.csv

for threshold in `seq 0 10 90`
do
	mkdir -p data
	rm -f data/*.log
	for numpar in `seq 1 10`
	do
		python3 -u faasproducer.py _testdata.ds2-small/ 2>&1 | tee -a data/experiment.log
		python3 -u faasmeasure.py $numpar False $threshold 2>&1 | tee -a data/experiment.log
	done
	mv data/ data-experiment/threshold-$threshold-ms
done

for baseline in all individual
do
	mkdir -p data
	rm -f data/*.log
	for numpar in `seq 1 10`
	do
		python3 -u faasproducer.py _testdata.ds2-small/ 2>&1 | tee -a data/experiment.log
		python3 -u faasmeasure.py $numpar False 0 $baseline 2>&1 | tee -a data/experiment.log
	done
	mv data/ data-experiment/baseline-$baseline
done
