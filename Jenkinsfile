pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    environment {
        IMAGE_NAME     = 'mental-health-app'
        CONTAINER_NAME = 'mental-health-container'
        PORT           = '9002'
    }

    stages {

        stage('Checkout Code') {
            steps {
                git branch: 'main',
                    credentialsId: 'learnfella-credentials',
                    url: 'https://github.com/Rajachellan/Mental-health-monitoring.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t ${IMAGE_NAME} .'
            }
        }

        stage('Deploy (Port 9002)') {
            steps {
                sh '''
                docker rm -f ${CONTAINER_NAME} || true
                docker run -d \
                    --name ${CONTAINER_NAME} \
                    -p ${PORT}:5000 \
                    --restart unless-stopped \
                    ${IMAGE_NAME}
                '''
            }
        }
    }

    post {
        success {
            echo "✅ Mental Health App is LIVE on port 9002"
        }
        failure {
            echo "❌ Deployment failed"
        }
        always {
            sh 'docker image prune -f || true'
        }
    }
}
