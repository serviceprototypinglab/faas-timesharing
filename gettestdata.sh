#!/bin/sh

folder=_testdata

echo "Downloading test data..."

if [ -d $folder ]
then
	echo "Skipping, test data already present. Remove folder $folder to renew."
	exit 0
fi

mkdir -p _testdata
cd _testdata

for link in `cat ../gettestdata.urls`
do
	wget -q $link -O `echo $link | md5sum | cut -d " " -f 1`.jpg
	echo -n .
done
echo
