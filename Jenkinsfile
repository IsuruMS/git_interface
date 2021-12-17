def srcBr = ""
def srcRep = ""
def trgBr = ""

pipeline {
    agent any
    stages {
        stage ('Git Checkout Repo') {
            steps {
                bat "rmdir /s /q git_interface"
                bat "git clone https://github.com/IsuruMS/git_interface.git"
            }
        }
        /*stage ('Install Requirements') {
            steps {
                bat "cd git_interface"
                bat "pip install -r requirements.txt"
            }
        }
        stage('Update') {
            steps {
                bat "cd git_interface"
                bat "python git_interface.py -l https://github.com/opencv"
            }
        }*/
        stage('Read Parameters') {
            steps {
                script {
                    srcBr = "%params.SOURCE%"
                    srcRep = "%params.TARGET%"
                    trgBr = "%params.REPO%"
                }
            }
        }
        stage ('Setup Parameters') {
            steps {
                script {
                    echo "Reading Parameters from settings.yaml"
                    data = readYaml file: "settings.yaml"

                    def srcList = []
                    def repList = []
                    for (def key in data.keySet()) {
                        if (repList.contains(key) == false) {
                            repList.add(key)
                        }
                        if (key != "token") {
                            for (def br in data[key]['branches']) {
                                if (srcList.contains(br) == false) {
                                    srcList.add(br)
                                }
                            }
                        }
                    }
                    println srcList
                    println repList
                    properties ([
                        parameters ([
                            choice(name: 'SOURCE', choices: srcList, description: 'Name of the source branch'),
                            choice(name: 'REPO', choices: repList, description: 'Name of the source repo'),
                            string(name: 'TARGET', defaultValue: '', description: 'Name of the target branch')
                        ])
                    ])
                }
            }
        }
        stage('Branching') {
            steps {
                bat "python git_interface.py -s %srcBr% -t %trgBr% -r %srcRep%"
            }
        }
    }
}