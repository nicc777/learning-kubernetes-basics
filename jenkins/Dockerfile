FROM jenkins/jenkins:lts

# Install dependcies as well as only the Docker client
USER root
RUN apt-get update && apt-get install -y python3 python3-setuptools python3-pip apt-transport-https ca-certificates curl gnupg-agent software-properties-common sudo
RUN curl -fsSL https://download.docker.com/linux/debian/gpg | apt-key add -
RUN add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/debian $(lsb_release -cs) stable"
RUN apt-get update
RUN apt-get install docker-ce-cli
RUN groupadd docker
RUN usermod -aG sudo jenkins

VOLUME /var/run/docker.sock

USER jenkins
