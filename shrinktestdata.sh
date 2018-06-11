#!/bin/sh

if [ -z $1 ]
then
	echo "Syntax: $0 <infolder>"
	exit 1
fi

mkdir $1-small

for i in $1/*
do
	fn=`basename $i`
	convert -scale 800 $i $1-small/$fn
done
