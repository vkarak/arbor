#!/bin/bash -l
#SBATCH --job-name='arbor-ci'
#SBATCH --partition=cscsci
#SBATCH -C gpu

commit=$1

module load reframe

../reframe/bin/reframe --system=daint:gpu -C ci/rfm-config.py -c ci/arbor_tests.py --prefix=$SCRATCH/arbor-ci-$commit --exec-policy=async -r
