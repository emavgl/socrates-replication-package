#!/bin/bash
#$ -N singularitytestfull10top-x
#$ -q st-tmp.q
#$ -l mf=4G
#$ -M eviglianisi@fbk.eu
#$ -m es
#$ -S /bin/bash

EXPERIMENTSDIR=$HOME/experiments
WORKINGDIR=$EXPERIMENTSDIR/testfull10top/x
singularity run --net --bind $EXPERIMENTSDIR/toptokens:/usr/src/app/inputs,$WORKINGDIR/output:/usr/src/app/output,$WORKINGDIR/testconf:/usr/src/app/testconf $EXPERIMENTSDIR/production.simg
