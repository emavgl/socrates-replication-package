#!/bin/bash
#$ -N singularitytestrandom10-x
#$ -q st-tmp.q
#$ -l mf=4G
#$ -M eviglianisi@fbk.eu
#$ -m es
#$ -S /bin/bash

EXPERIMENTSDIR=$HOME/experiments
WORKINGDIR=$EXPERIMENTSDIR/testrandom10/x
singularity run --net --bind $EXPERIMENTSDIR/inputs:/usr/src/app/inputs,$WORKINGDIR/output:/usr/src/app/output,$WORKINGDIR/testconf:/usr/src/app/testconf $EXPERIMENTSDIR/production.simg
