// This is a Jenkins pipeline file used to perform a static code analysis.
// For the status to be visible on GitHub, you have to add "seedlabs-ateam" collaborator & add "Jenkins (Git plugin)"
// service to your git repository.


@Library('JenkinsMain@2.19.20')_

pipelinePythonSCA(
    agentLabel: 'docker',
    pythonVersion: '3.10',
    installFromSetup: true,
    runPylint: false,
    runUnitTests: true,
    unitTestRunner: 'py.test',
    packages: [".[tests]"],
)
