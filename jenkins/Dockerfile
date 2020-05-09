FROM jenkins/jenkins:lts

# Install dependcies to build our app 
USER root
RUN apt-get update && apt-get install -y python3 python3-setuptools python3-pip apt-transport-https ca-certificates curl gnupg-agent software-properties-common sudo postgresql-client

# Install only the Docker CLI (no daemon - we will use the host daemon via Unix sockets)
RUN curl -fsSL https://download.docker.com/linux/debian/gpg | apt-key add -
RUN add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/debian $(lsb_release -cs) stable"
RUN apt-get update
RUN apt-get install docker-ce-cli

# Allow Jenkins to run the docker command as root without requiring a password. ($ sudo docker ....)
COPY sudoers /etc/sudoers
RUN chown root.root /etc/sudoers
RUN chmod 440 /etc/sudoers

# Allows us to hook-up to the host Docker daemon 
VOLUME /var/run/docker.sock

USER jenkins
