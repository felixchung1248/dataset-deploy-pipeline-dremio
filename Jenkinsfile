pipeline {
    agent any

    parameters {
        string(name: 'DATASET_NAME', description: 'Dataset name')
		string(name: 'SCHEMA_NAME', description: 'Schema name')
        string(name: 'TICKET_ID', description: 'Ticket ID')
		string(name: 'DATASET_OWNER', description: 'Dataset owner')
        string(name: 'DATASET_DESCRIPTION', description: 'Dataset description')
    }

    stages {
        stage('Pre-flight Check') {
            steps {
                script {
                    if (!params.DATASET_NAME) {
                        error "The DATASET_NAME parameter is missing. Please provide the dataset name."
                    }
					if (!params.SCHEMA_NAME) {
                        error "The SCHEMA_NAME parameter is missing. Please provide the schema name."
                    }
                    if (!params.TICKET_ID) {
                        error "The TICKET_ID parameter is missing. Please provide the ticket ID."
                    }
                    if (!params.DATASET_OWNER) {
                        error "The DATASET_OWNER parameter is missing. Please provide the dataset owner."
                    }
                    if (!params.DATASET_DESCRIPTION) {
                        error "The DATASET_DESCRIPTION parameter is missing. Please provide the dataset description."
                    }
                }
            }
        }

        stage('Run Dataset deploy') {
            steps {
                withCredentials([
                    usernamePassword(credentialsId: 'dremio-sandbox-credentials', 
                                     usernameVariable: 'DREMIO_SANDBOX_USR', 
                                     passwordVariable: 'DREMIO_SANDBOX_PW')
					,usernamePassword(credentialsId: 'dremio-prod-credentials', 
                                     usernameVariable: 'DREMIO_PROD_USR', 
                                     passwordVariable: 'DREMIO_PROD_PW')
                ]) {
                    sh """
                        python3 ${env.WORKSPACE}/cloner.py schema=${env.SCHEMA_NAME} dataset=${env.DATASET_NAME}
                    """
                }
            }
        }
		
		stage('Deploy data catalog dataset') {
            steps {
                withCredentials([
                    usernamePassword(credentialsId: 'zammad-credentials', 
                                     usernameVariable: 'ZAMMAD_USR', 
                                     passwordVariable: 'ZAMMAD_PW')
                ]) {					
                    sh """
                        python3 ${env.WORKSPACE}/data-catalog-deploy.py ticket_id=${env.TICKET_ID} dataset=${env.DATASET_NAME} dataset_owner=${env.DATASET_OWNER} dataset_description="${env.DATASET_DESCRIPTION} schema=${env.SCHEMA_NAME}"
                    """
                }
             }
        }
    }
}

   // post {
   //     always {
   //         // Optional: clean up
   //         // cleanWs()
   //     }
   // }

