#!/bin/bash -l
#SBATCH --job-name='arbor-ci'
#SBATCH --partition=cscsci
#SBATCH -C gpu

rfm_exec=$1

module load reframe

$rfm_exec --system=daint:gpu -C ci/rfm-config.py -c ci/arbor_tests.py --prefix=$SCRATCH/rfm-stage --exec-policy=async -r
