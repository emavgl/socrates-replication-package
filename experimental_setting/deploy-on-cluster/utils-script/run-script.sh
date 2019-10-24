#!/bin/bash

if [ "$#" -ne 1 ]; then
    echo "Usage: bash submit-scripts.sh <input-dir>"
fi

DIR=$1/*.sh
for SCRIPTPATH in $DIR; do
    echo $SCRIPTPATH
    qsub $SCRIPTPATH
done
