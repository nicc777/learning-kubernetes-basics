
- [1. Objectives of the Scenario](#1-objectives-of-the-scenario)
- [2. Technology & Patterns](#2-technology--patterns)
- [3. Step-by-Step Demo Walk Through](#3-step-by-step-demo-walk-through)
  - [3.1 Prepare a docker environment](#31-prepare-a-docker-environment)
  - [3.2 Build a custom Jenkins container to suite the application environment](#32-build-a-custom-jenkins-container-to-suite-the-application-environment)
- [4. Scenario Discussion](#4-scenario-discussion)
  - [4.1 Trail-Map Progress](#41-trail-map-progress)
  - [4.2 Cloud-Native Principles Progress](#42-cloud-native-principles-progress)
- [5. References](#5-references)

# 1. Objectives of the Scenario

In this scenario a release branch will be set-up with monitoring/triggers for changes in the `appsrc-develop` branch.

Ideally whenever there is an approved pull request (PR) into the release branch, the automation needs to kick in.

What needs to be build is the following:

1. If the Base Docker image have changed, build a new base
2. Run the application build script that will also produce a new application image

However, for the lab environment it is not possible to use web-hooks. In a production environment where you would use your own Git repository internally you would need to figure out how to set this up yourself.

This section will use the configuration that will fetch all updates from the relevant branch and then use some basic tests to see if anything have changed, and then build new Docker images based on those tests, as required. The job will be configured to run once an hour at least, but in Jenkins you can also trigger the job manually.

# 2. Technology & Patterns

For this scenario a build server is required and since [Jenkins](https://www.jenkins.io) is still widely used, I will stick to this trusty old workhorse.

Ideally you would use web hooks to trigger a build any time a merge pull request into `appsrc-develop` is approved.

# 3. Step-by-Step Demo Walk Through

These steps are executed on a system where you will host your CI/CD pipeline. For me that is on my `Server` and the commands shown are executed from that server.

I will deploy the official [Docker version of Jenkins](https://hub.docker.com/r/jenkins/jenkins).

## 3.1 Prepare a docker environment

In order to run Jenkins in Docker, a number of steps need to be taken since we want to build docker images from Jenkins, which itself will be running in Docker.

Following the guidance from the official Jenkins documentation, you can relatively safely run the following:

```bash
(venv) $ docker network create jenkins
(venv) $ docker volume create jenkins-data
(venv) $ docker volume inspect jenkins-data
[
    {
        "CreatedAt": "2020-05-03T12:01:18+02:00",
        "Driver": "local",
        "Labels": {},
        "Mountpoint": "/var/lib/docker/volumes/jenkins-data/_data",
        "Name": "jenkins-data",
        "Options": {},
        "Scope": "local"
    }
]
```

## 3.2 Build a custom Jenkins container to suite the application environment

There is a branch called `jenkins` with detailed instructions in the `README.md` file.

# 4. Scenario Discussion

I initially started out with the official Jenkins recommendation [as documented here](https://www.jenkins.io/doc/book/installing/#downloading-and-running-jenkins-in-docker), but after some trial and error as well as [some more reading](https://jpetazzo.github.io/2015/09/03/do-not-use-docker-in-docker-for-ci/), I decided on the final approach as documented here.

## 4.1 Trail-Map Progress

| Category                               | Technologies & Patterns Used | Progress and other notes |
|----------------------------------------|------------------------------|--------------------------|
| Containers (Docker)                    | Docker | Current application and database have been containerized |
| CI/CD                                  | Jenkins | The `CI` portion is now implemented. A Docker image is built on the `Server`. |
| Orchestration & Application Definition | n/a                          | not started yet          |
| Observability and Analysis             | n/a                          | not started yet          |
| Service Proxy, Discovery & Mesh        | n/a                          | not started yet          |
| Networking, Policy & Security          | n/a                          | not started yet          |
| Distributed Database & Storage         | n/a                          | not started yet          |
| Streaming & Messaging                  | n/a                          | not started yet          |
| Container Registry & Runtime           | n/a                          | not started yet          |
| Software Distribution                  | n/a                          | not started yet          |

## 4.2 Cloud-Native Principles Progress

| Factor                        | Progress and Discussion |
|-------------------------------|-------------------------|
| Code Base                     | Source code is tracked in Git. Each version will have it's own branch. Each version can be independently built and deployed. |
| Dependencies                  | As part of the containerization effort, all dependencies are defined in the base and main application Docker files. There is still potential for finding a more lightweight base image to start with. The approach takes was to use the base Docker configuration to install all required software and dependencies. This image is typically build once as it will take the most time to build. The application Docker image is essentially just an installation of the latest Python application package and the build is relatively quick and is perfectly geared to be done many times. |
| Configurations                | Configuration is now done entirely through environment variable defined in the Docker configuration files. Configuration parameters can be set when launching the application. |
| Backing Services              | The database server has also been containerized. The application is simple enough to not rely too much on database versions and therefore almost any version of PostgreSQL can be used. Changing from PostgreSQL to something else is relatively easy as long as that something else is supported by [SQLAlchemy](https://www.sqlalchemy.org) and only minor code changes will then be required. If this will happen often (which it shouldn't), more configuration options and a more dynamic dependency system can be considered. |
| Build, Release, Run           | The `CI` portion of the `CI/CD` pipeline have been implemented with a Jenkins build that will produce an application Docker image on the `Server` |
| Processes                     | No active effort have been made to ensure the application is truly stateless. Future testing will prove this and the application will be adjusted accordingly. At the moment the application should be able to run with multiple instances. |
| Port Binding                  | This is considered completed as the application is hosted in the container and exposed via [gunicorn](https://gunicorn.org). |
| Concurrency                   | Untested but assumed to not be a problem. Will revisit during more testing in future scenarios. |
| Disposability                 | Untested but assumed to not be a problem. Will revisit during more testing in future scenarios. |
| Dev/Prod Parity               | No progress yet         |
| Logging                       | Logs are now logged to a file as well as `STDOUT`, and can be accessed via the Docker API. No log events are published yet and more work remain. |
| Admin Processes               | No progress yet         |
| API First                     | Through the use of [connexion](https://github.com/zalando/connexion) the application have been implemented with an API first principle from the start. This is considered DONE. |
| Telemetry                     | No progress yet         |
| Authentication/ Authorization | No progress yet. The application currently completely trusts the Application Server and relies on external configuration to prevent other unauthorized services connecting to it. |

# 5. References

* [Some thoughts on why using Docker in Docker is a bad idea for building images](https://jpetazzo.github.io/2015/09/03/do-not-use-docker-in-docker-for-ci/)

