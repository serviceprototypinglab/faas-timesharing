#!/bin/sh

if [ -z $1 ]
then
	echo "Syntax: $0 <infolder>"
	exit 1
fi

oname=$1
tname=`basename $1`-small

mkdir $tname

for i in $oname/*.jpg
do
	fn=`basename $i`
	convert -scale 800 $i $tname/$fn
done
