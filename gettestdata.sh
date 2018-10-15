#!/bin/sh

folder=_testdata
ds=ds2

if [ ! -z $1 ]
then
	ds=$1
fi

echo "Downloading test data ($ds)..."

if [ -d $folder.$ds ]
then
	echo "Skipping, test data already present. Remove folder $folder.$ds to renew."
	exit 0
fi

mkdir -p _testdata.$ds
cd _testdata.$ds

for link in `cat ../gettestdata.$ds.urls`
do
	wget -qc $link -O `echo $link | md5sum | cut -d " " -f 1`.jpg
	echo -n .
done
echo
