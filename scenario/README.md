
- [1. Objectives of the Scenario](#1-objectives-of-the-scenario)
- [2. Technology & Patterns](#2-technology--patterns)
- [3. Step-by-Step Demo Walk Through](#3-step-by-step-demo-walk-through)
  - [3.1 Starting the Docker Registry Service](#31-starting-the-docker-registry-service)
  - [3.2 Adjusting Jenkins to push newly built images to the registry](#32-adjusting-jenkins-to-push-newly-built-images-to-the-registry)
- [4. Scenario Discussion](#4-scenario-discussion)
  - [4.1 Trail-Map Progress](#41-trail-map-progress)
  - [4.2 Cloud-Native Principles Progress](#42-cloud-native-principles-progress)
- [5. References](#5-references)

# 1. Objectives of the Scenario

Create a private Docker registry to push new builds to.

# 2. Technology & Patterns

There are many scenarios within the context of organizations where you would prefer to not expose your Docker images to public repositories. For this reason, hosting a private registry makes a lot of sense.

In this scenario, a private registry will be created according to the [Docker private registry documentation](https://docs.docker.com/registry/deploying/) and the `CI` pipeline in the `jenkins` branch will be updated to publish new images to this registry.

# 3. Step-by-Step Demo Walk Through

The steps are fairly basic since Docker already has a out-of-the-box solution for quickly setting up a registry.

## 3.1 Starting the Docker Registry Service

Run the following command:

```bash
(venv) $ docker run -d -p 0.0.0.0:5000:5000 --restart=always --name registry registry:2
```

__Note__: I have setup the registry to listen on the Ethernet interface in order to expose the service to my entire LAN. You may need to adjust this to suite your needs.

__Security Note__: The [documentation](https://docs.docker.com/registry/deploying/) has a lot more detail around various scenarios, including TLS certificates and authentication. Again, adjust for your needs.

## 3.2 Adjusting Jenkins to push newly built images to the registry

TODO

# 4. Scenario Discussion

TODO

In each scenario we will map our progress against the Cloud-Native Trail Map and against the Cloud-Native Principles.

## 4.1 Trail-Map Progress

| Category                               | Technologies & Patterns Used | Progress and other notes |
|----------------------------------------|------------------------------|--------------------------|
| Containers (Docker)                    | n/a                          | not started yet          |
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
| Code Base                     | No progress yet         |
| Dependencies                  | No progress yet         |
| Configurations                | No progress yet         |
| Backing Services              | No progress yet         |
| Build, Release, Run           | No progress yet         |
| Processes                     | No progress yet         |
| Port Binding                  | No progress yet         |
| Concurrency                   | No progress yet         |
| Disposability                 | No progress yet         |
| Dev/Prod Parity               | No progress yet         |
| Logging                       | No progress yet         |
| Admin Processes               | No progress yet         |
| API First                     | No progress yet         |
| Telemetry                     | No progress yet         |
| Authentication/ Authorization | No progress yet         |

# 5. References

* [Docker documentation on deploying a registry](https://docs.docker.com/registry/deploying/)
* [Docker registry on Docker Hub](https://hub.docker.com/_/registry)