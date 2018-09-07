stage('Testing') {
    node('scs_daintvm1') {
        dir('reframe') {
            checkout([$class: 'GitSCM', branches: [[name: 'master']],
                extensions: [[$class: 'WipeWorkspace']], 
                userRemoteConfigs: [[url: 'https://github.com/eth-cscs/reframe.git']]])
        }
        dir('arbor') {
            uniqueID = "${env.ghprbActualCommit[0..6]}-${env.BUILD_ID}"
            checkout scm
            sh("""#!/bin/bash -l
                  git submodule update --init --recursive
                  sbatch --wait -o arbor-ci.out ci/cscs-daint-gpu.sh ${uniqueID}
                  exit_status=\$?
                  cat arbor-ci.out
                  exit \$exit_status
               """)
            archiveArtifacts 'arbor-ci.out,reframe.out,reframe.log'
        }
        deleteDir()
    }
}
