stage('Testing') {
    node('scs_daintvm1') {
        dir('reframe') {
            checkout([$class: 'GitSCM', branches: [[name: 'master']],
                extensions: [[$class: 'WipeWorkspace']], 
                userRemoteConfigs: [[url: 'https://github.com/eth-cscs/reframe.git']]])
        }
        dir('arbor') {
            checkout([$class: 'GitSCM', branches: [[name: 'ci/reframe-tests']],
                extensions: [[$class: 'WipeWorkspace'],
                             [$class: 'SubmoduleOption', disableSubmodules: false,
                              recursiveSubmodules: true, trackingSubmodules: true]],
                userRemoteConfigs: [[url: 'https://github.com/vkarak/arbor.git']]])
            sh("""#!/bin/bash -l
                  sbatch --wait -o arbor-ci.out ci/cscs-daint-gpu.sh ../reframe/bin/reframe
                  cat arbor-ci.out
               """)
        }
        deleteDir()
    }
}
