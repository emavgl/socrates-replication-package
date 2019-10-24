#!/bin/bash

if [ "$#" -ne 3 ]; then
    echo "Usage: bash copy-folder-n-times.bash <input-dir> <output-dir> <times>"
fi

INPUTDIR=$1
OUTPUTDIR=$2
TIMES=$(($3-1))

for i in $(seq 0 $TIMES); do
    echo $OUTPUTDIR/$i
    mkdir -p $OUTPUTDIR/$i
    cp -r $INPUTDIR/* $OUTPUTDIR/$i
done
