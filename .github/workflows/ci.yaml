name: Java CI
on: [push]
jobs:
  jenkins-container-pipeline:
    runs-on: ubuntu-latest
    container:
      image: ghcr.io/jenkinsci/jenkinsfile-runner:master
    steps:
      - uses: actions/checkout@v2
      - uses:
          jenkinsci/jfr-container-action@master
        with:
          command: run
          jenkinsfile: Jenkinsfile
          pluginstxt: plugins.txt
          jcasc: jcasc.yml
