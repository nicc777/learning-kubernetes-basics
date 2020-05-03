
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

TODO

## 4.2 Cloud-Native Principles Progress

TODO

# 5. References

* [n-Tier Architecture Overview from Microsoft](https://docs.microsoft.com/en-us/azure/architecture/guide/architecture-styles/n-tier)
* [Python](https://www.python.org/)
* [Flask](https://flask.palletsprojects.com/en/1.1.x/) web framework
* [PostgreSQL Database Server](https://www.postgresql.org/)
* [Docker](https://docs.docker.com/)
* [REST](https://restfulapi.net/)
* [OpenAPI v3](https://swagger.io/specification/)
