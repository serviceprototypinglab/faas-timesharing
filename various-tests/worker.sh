for i in $(seq 1 10)
do
	(aws lambda invoke --function-name contextual /tmp/_out$i >/dev/null && \
	echo -n $i: && \
	cat /tmp/_out$i && \
	echo && \
	rm /tmp/_out$i) &
done
