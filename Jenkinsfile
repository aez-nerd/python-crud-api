pipeline {
    agent any

    environment {
        PYTHONUNBUFFERED = '1'
        REGISTRY_NAME = 'python-crud-api'
        CONTAINER_NAME = 'production-api-container'
        PORT_MAPPING = '5000:5000'
        VOLUME_NAME = 'production-api-data'
    }

    stages {
        stage('1. Checkout Code') {
            steps {
                echo 'Checking out source code from GitHub'
                checkout scm
                script {
                    env.GIT_COMMIT_SHORT = sh(
                        script: 'git rev-parse --short HEAD',
                        returnStdout: true
                    ).trim()
                    echo "Checked out commit SHA: ${env.GIT_COMMIT_SHORT}"
                }
            }
        }

        stage('2. Code Syntax & Linting') {
            steps {
                sh 'python3 -m py_compile app.py test_app.py'
                sh 'flake8 app.py test_app.py --max-line-length=100 || true'
            }
        }

        stage('2b. Automated Unit Tests') {
            steps {
                sh 'python3 -m unittest discover -v -s . -p "test_*.py"'
            }
        }

        stage('3. Build Docker Image') {
            steps {
                sh '''
                    if docker image inspect ${REGISTRY_NAME}:latest >/dev/null 2>&1; then
                        docker tag ${REGISTRY_NAME}:latest ${REGISTRY_NAME}:previous
                    fi
                    docker build -t ${REGISTRY_NAME}:${BUILD_NUMBER} .
                    docker tag ${REGISTRY_NAME}:${BUILD_NUMBER} ${REGISTRY_NAME}:${GIT_COMMIT_SHORT}
                    docker tag ${REGISTRY_NAME}:${BUILD_NUMBER} ${REGISTRY_NAME}:latest
                '''
            }
        }

        stage('4. Automated Deployment') {
            steps {
                sh '''
                    docker stop ${CONTAINER_NAME} || true
                    docker rm ${CONTAINER_NAME} || true
                    docker volume create ${VOLUME_NAME}
                    docker run -d \\
                        --name ${CONTAINER_NAME} \\
                        -p ${PORT_MAPPING} \\
                        -v ${VOLUME_NAME}:/var/lib/backend_data \\
                        ${REGISTRY_NAME}:latest
                '''
            }
        }

        stage('5. Health Check') {
            steps {
                sh 'sleep 3'
                sh 'curl -fsS http://localhost:5000/health'
                sh 'docker logs --tail 20 ${CONTAINER_NAME}'
            }
        }
    }

    post {
        success {
            echo "Pipeline completed successfully. Deployed ${REGISTRY_NAME}:${BUILD_NUMBER} (SHA: ${env.GIT_COMMIT_SHORT})."
        }
        failure {
            echo 'Pipeline failed. Executing rollback check and inspecting Console Output.'
            sh '''
                if docker image inspect ${REGISTRY_NAME}:previous >/dev/null 2>&1; then
                    echo "Rolling back container ${CONTAINER_NAME} to ${REGISTRY_NAME}:previous..."
                    docker stop ${CONTAINER_NAME} || true
                    docker rm ${CONTAINER_NAME} || true
                    docker run -d \\
                        --name ${CONTAINER_NAME} \\
                        -p ${PORT_MAPPING} \\
                        -v ${VOLUME_NAME}:/var/lib/backend_data \\
                        ${REGISTRY_NAME}:previous
                fi
            '''
        }
    }
}
