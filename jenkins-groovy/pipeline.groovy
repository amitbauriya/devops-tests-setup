@Library(['github.com/shared-library']) _

pipeline {
    agent {
        node {
            label 'spring'
        }
    }
    tools {
        jdk 'OpenJDK 16'
    }

  options {
    timeout(time: 60, unit: 'MINUTES')
    timestamps()
    buildDiscarder(logRotator(numToKeepStr: '5'))
  }

  stages {

    stage('checkout') {
        steps {
                script {
                    git branch:"${BRANCH_NAME}",
                        credentialsId: "${git_credential}",
                        url: "http://${repo_url}"
                    commitId = sh (script: 'git rev-parse --short HEAD ${GIT_COMMIT}', returnStdout: true).trim()
                }
        }
    }

    stages {
        stage('Clean builds if any') {
            steps {
                echo 'Cleaning leftovers from previous builds'
                sh "chmod +x -R ${env.WORKSPACE}"
                sh './gradlew clean'
            }
        }

        stage('Compile code') {
            steps {
                echo 'COMPILING JAVA'
                sh './gradlew assemble'
            }
        }

        stage('Code analysis') {
            steps {
                echo 'Running Static Code Analysis'

                echo 'Checking style'
                sh './gradlew checkstyleMain'

                echo 'Checking duplicated code'
                sh './gradlew cpdCheck'

                echo 'Checking bugs'
                sh './gradlew spotbugsMain'

                echo 'Checking code standard'
                sh './gradlew pmdMain'
            }
        }

        //S3 Bucket upload requires this plugin https://github.com/jenkinsci/pipeline-aws-plugin
        stage("Image build"){
            steps {
                script {
                    sh "docker images"
                    dir("${base_imagename}"){
                        docker.build "${base_imagename}"
                    }
                    dir("${api_imagename}"){
                        docker.build "${api_imagename}"
                    }
                    dir("${auth_imagename}"){
                        docker.build "${auth_imagename}"
                    }
                    sh "docker images"
                }
            }
        }
        stage("Compress docker images to gz"){
            steps{
                sh "mkdir ${TAG_NAME}"
                dir("${TAG_NAME}"){
                    sh "docker save ${api_imagename}:latest > ${api_imagename}-${TAG_NAME}.tar.gz"
                    sh "docker save ${auth_imagename}:latest > ${auth_imagename}-${TAG_NAME}.tar.gz"
                }
            }
        }        
        stage("Upload to s3"){
            steps{
                withAWS(region:"${region}", credentials:"${aws_credential}){
                    s3Upload(file:"${TAG_NAME}", bucket:"${bucket}", path:"${TAG_NAME}/")
                }    
        }
        
        
    }

    post {
        always {
            cleanWs()
            dir("${env.WORKSPACE}@tmp") {
              deleteDir()
            }
            dir("${env.WORKSPACE}@script") {
              deleteDir()
            }
            dir("${env.WORKSPACE}@script@tmp") {
              deleteDir()
            }
            sh "docker rmi ${base_imagename}"
            sh "docker rmi ${api_imagename}"
            sh "docker rmi ${auth_imagename}"
        }
    }    
    
    
}
