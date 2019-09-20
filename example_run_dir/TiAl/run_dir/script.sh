#!/bin/bash
#$ -pe smp 1 
#$ -l h_rt=4:00:00
#$ -q 'tomsk|any|orinoco'
#$ -S /bin/bash
#$ -N job
#$ -j yes
#$ -cwd

export JULIA_NUM_THREADS=1
python ../../../scripts/run-model-test.py SHIP_test Zmethod_TiAl -s TiAl -f
