#!/usr/bin/env groovy

def dirPrefix = 'reframe-ci'
def loginBash = '#!/bin/bash -l'
def machinesList = ['daint', 'dom']
def machinesToRun = machinesList
def uniqueID

stage('Initialization') {
    node('master') {
        try {
            uniqueID = "${env.ghprbActualCommit[0..6]}-${env.BUILD_ID}"
            echo 'Environment Variables:'
            echo sh(script: 'env|sort', returnStdout: true)

            def githubComment = env.ghprbCommentBody
            if (githubComment == 'null') {
                machinesToRun = machinesList
                currentBuild.result = 'SUCCESS'
                return
            }

            def splittedComment = githubComment.split()
            if (splittedComment.size() < 3) {
                println 'No machines were found. Aborting...'
                currentBuild.result = 'ABORTED'
                return
            }
            if (splittedComment[1] != 'retry') {
                println "Invalid command ${splittedComment[1]}. Aborting..."
                currentBuild.result = 'ABORTED'
                return
            }
            if (splittedComment[2] == 'all') {
                machinesToRun = machinesList
                currentBuild.result = 'SUCCESS'
                return
            }

            machinesRequested = []
            for (i = 2; i < splittedComment.size(); i++) {
                machinesRequested.add(splittedComment[i])
            }

            machinesToRun = machinesRequested.findAll({it in machinesList})
            if (!machinesToRun) {
                println 'No machines were found. Aborting...'
                currentBuild.result = 'ABORTED'
                return
            }

            currentBuild.result = 'SUCCESS'
        } catch(err) {
            println err.toString()
            if (err.toString().contains('exit code 143')) {
                currentBuild.result = "ABORTED"
            }
            else if (err.toString().contains('Queue task was cancelled')) {
                currentBuild.result = "ABORTED"
            }
            else {
                currentBuild.result = "FAILURE"
            }
        }
    }
}

if (currentBuild.result != 'SUCCESS') {
    println "Initialization failed (${currentBuild.result}). Exiting..."
    return
}

def builds = [:]
stage('Unittest') {
    for (mach in machinesToRun) {
        def machineName = mach
        builds[machineName] = {
            node(machineName) {
                def scratch = sh(returnStdout: true,
                                 script: """${loginBash}
                                            echo \$SCRATCH""").trim()
                def reframeDir = "${scratch}/${dirPrefix}-${machineName}-${uniqueID}"
                dir(reframeDir) {
                    checkout scm
                    sh("""${loginBash}
                          module load reframe
                          reframe --prefix=${reframeDir} -c ci/reframe/arbor_tests.py --exec-policy=async -r""")
                }
            }
        }
    }

    try {
        parallel builds
        currentBuild.result = "SUCCESS"
    } catch(err) {
        if (err.toString().contains('exit code 143')) {
            currentBuild.result = "ABORTED"
            println "The Unittest was cancelled. Aborting....."
        }
        else if (err.toString().contains('Queue task was cancelled')) {
            currentBuild.result = "ABORTED"
            println "The Queue task was cancelled. Aborting....."
        }
        else {
            currentBuild.result = "FAILURE"
            println "The Unittest failed. Exiting....."
        }
    }
}

builds = [:]
stage('Cleanup') {
    if (currentBuild.result != 'SUCCESS') {
        println 'Not executing "Cleanup" Stage'
        return
    }
    else {
        for (mach in machinesToRun) {
            def machineName = mach
            builds[machineName] = {
                node(machineName) {
                    def scratch = sh(returnStdout: true,
                                     script: """$loginBash
                                                echo \$SCRATCH""").trim()
                    def reframeDir = "${scratch}/${dirPrefix}-${machineName}-${uniqueID}"
                    sh("""${loginBash}
                          rm -rf ${reframeDir}
                          date""")

                }
            }
        }
        try {
            parallel builds
            currentBuild.result = "SUCCESS"
        } catch(err) {
            if (err.toString().contains('exit code 143')) {
                currentBuild.result = "ABORTED"
                println "The Cleanup was cancelled. Aborting....."
            }
            else if (err.toString().contains('Queue task was cancelled')) {
                currentBuild.result = "ABORTED"
                println "The Queue task was cancelled. Aborting....."
            }
            else {
                currentBuild.result = "FAILURE"
                println "The Cleanup failed. Exiting....."
            }
        }
    }
}

def staleCleanupInterval = 3
builds = [:]
stage('Cleanup Stale') {
     for (mach in machinesToRun) {
        def machineName = mach
        builds[machineName] = {
            node(machineName) {
                def scratch = sh(returnStdout: true,
                                 script: """${loginBash}
                                            echo \$SCRATCH""").trim()
                sh("""${loginBash}
                      find ${scratch} -maxdepth 1 -name 'reframe-ci*' -ctime +${staleCleanupInterval} -type d -exec printf 'Removing  %s\\n' {} +
                      find ${scratch} -maxdepth 1 -name 'reframe-ci*' -ctime +${staleCleanupInterval} -type d -exec rm -rf {} +""")
            }
        }
    }

    try {
        parallel builds
        currentBuild.result = "SUCCESS"
    } catch(err) {
        if (err.toString().contains('exit code 143')) {
            currentBuild.result = "ABORTED"
            println "The Build step was cancelled. Aborting....."
        }
        else if (err.toString().contains('Queue task was cancelled')) {
            currentBuild.result = "ABORTED"
            println "The Queue task was cancelled. Aborting....."
        }
        else {
            currentBuild.result = "FAILURE"
            println "The Build step failed. Exiting....."
        }
    }
}
