#!/bin/sh
#SBATCH -A CSANYI-SL4-CPU
#SBATCH -p skylake
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --time=12:00:00

module load castep

python ../../../scripts/run-model-test.py CASTEP bulk_Ti_bcc -s TiAl -f
python ../../../scripts/run-model-test.py CASTEP bulk_Ti_hcp -s TiAl -f
