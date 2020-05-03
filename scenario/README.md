
- [1. Objectives of the Scenario](#1-objectives-of-the-scenario)
- [2. Technology & Patterns](#2-technology--patterns)
- [3. Step-by-Step Demo Walk Through](#3-step-by-step-demo-walk-through)
- [4. Scenario Discussion](#4-scenario-discussion)
  - [4.1 Trail-Map Progress](#41-trail-map-progress)
  - [4.2 Cloud-Native Principles Progress](#42-cloud-native-principles-progress)
- [5. References](#5-references)

# 1. Objectives of the Scenario

In this scenario we will ensure that you are starting of with a working application deployed in a Docker container. You could also run the application outside a container to more accurately simulate a n-Tier application, but since there are not that much difference in the deployment, we will jump right into it.

The application relies on a PostgreSQL database, which will also be deployed as a Docker container.

This scenario represents a starting point that many projects may follow, which is to containerize an application. Nothing much really happens in terms of the original source code. The aim is to get the application running in a Docker container with as little fuss as possible.

# 2. Technology & Patterns

Technology stack for this scenario:

* Docker
* Python
  * Flask web framework
* PostgreSQL Database Server

Important patterns to consider in this scenario:

* n-Tier architecture
* REST services
  * OpenAPI v3

# 3. Step-by-Step Demo Walk Through

The application source code, warts-and-all, with a detailed README to get the application going, is all available in the source branch. You can issue the following commands to check out that branch and follow the README instructions to build and run the Docker containers:

```bash
(venv) $ git checkout appsrc-0.0.1
```

And next you can open the `app-src/README.md` file and follow the instructions.

# 4. Scenario Discussion

At minimum you have a running service in a Docker container, together with a database also containerized.

The project at this stage has a number of obvious holes. There are no unit tests and testing of the services was done manually. Keep in mind the back story that this was a quick 1x sprint effort to quickly get a notes services deployed. This is common, and the reason why I have set up my learning environment as it is very likely for many projects to follow a similar pattern. The Cloud-Native alignment and required changes will happen next.

In each scenario we will map our progress against the Cloud-Native Trail Map and against the Cloud-Native Principles.

## 4.1 Trail-Map Progress

| Category                               | Technologies & Patterns Used | Progress and other notes |
|----------------------------------------|------------------------------|--------------------------|
| Containers (Docker)                    | Docker | Current application and database have been containerized |
| CI/CD                                  | n/a                          | not started yet          |
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
| Build, Release, Run           | No pipeline have been set-up yet. |
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

* [n-Tier Architecture Overview from Microsoft](https://docs.microsoft.com/en-us/azure/architecture/guide/architecture-styles/n-tier)
* [Python](https://www.python.org/)
* [Flask](https://flask.palletsprojects.com/en/1.1.x/) web framework
* [PostgreSQL Database Server](https://www.postgresql.org/)
* [Docker](https://docs.docker.com/)
* [REST](https://restfulapi.net/)
* [OpenAPI v3](https://swagger.io/specification/)
