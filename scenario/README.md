
- [1. Objectives of the Scenario](#1-objectives-of-the-scenario)
- [2. Technology & Patterns](#2-technology--patterns)
- [3. Step-by-Step Demo Walk Through](#3-step-by-step-demo-walk-through)
  - [3.1. Starting the Docker Registry Service](#31-starting-the-docker-registry-service)
  - [3.2. Adjusting Jenkins to push newly built images to the registry](#32-adjusting-jenkins-to-push-newly-built-images-to-the-registry)
  - [3.3. Testing the build](#33-testing-the-build)
  - [3.4. Verifying the published image](#34-verifying-the-published-image)
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

## 3.1. Starting the Docker Registry Service

Run the following command:

```bash
(venv) $ docker run -d -e REGISTRY_STORAGE_DELETE_ENABLED=true -p 0.0.0.0:5000:5000 --restart=always --name registry registry:2
```

__Note__: I have setup the registry to listen on the Ethernet interface in order to expose the service to my entire LAN. You may need to adjust this to suite your needs.

__Note__: In order to ENABLE deletion from the registry, you have to start it with the `-e REGISTRY_STORAGE_DELETE_ENABLED=true` parameter.

__Security Note__: The [documentation](https://docs.docker.com/registry/deploying/) has a lot more detail around various scenarios, including TLS certificates and authentication. Again, adjust for your needs.

__Important__: I had to experiment with several options to enable deletion of images on the registry. It seems that the parameter name tends to have changed over time, so there are more than one option. The one listed here was accurate as of 10 May 2020. 

## 3.2. Adjusting Jenkins to push newly built images to the registry

On the `Server`, in order for the Docker CLI (client app) to talk to this specific registry, we need to configure the client to allow HTTP communications. If you do not do that, you may see the following error in your build logs:

```text
Get https://192.168.0.160:5000/v2/: http: server gave HTTP response to HTTPS client
```

In order to do that, you must edit the config file `/etc/docker/daemon.json`. My config file looks like this:

```json
{
    "debug": false,
    "insecure-registries" : [
	    "localhost:5000",
	    "127.0.0.1:5000",
	    "192.168.0.160:5000"
    ]
}
```

__Note__: You may need to do this on every system that need to connect to the private registry

__Note__: Not sure if it's 100% necessary, but I did restart the Docker daemon. When you do that, make sure both the registry and jenkins are running again:

```bash
$ docker container ls
CONTAINER ID        IMAGE               COMMAND                  CREATED             STATUS              PORTS                                              NAMES
abd1bed6bc30        registry:2          "/entrypoint.sh /etc…"   51 minutes ago      Up 16 seconds       0.0.0.0:5000->5000/tcp                             registry
85b71ca6fed1        jenkins-custom      "/sbin/tini -- /usr/…"   28 hours ago        Up 1 second         0.0.0.0:50000->50000/tcp, 0.0.0.0:8085->8080/tcp   jenkins-coolapp-builder
```

## 3.3. Testing the build

In order to test a build, you may need to force a build. Assuming you have attempted a previous Jenkins build, you have two options:

1. Delete the `workspace` and manually run a build again (this will rebuild both the base and app images - takes a bit longer, but perfectly ok); or
2. Reset the checksum file used by the build script (shown below):

```bash
$ docker exec -it jenkins-coolapp-builder bash
jenkins@85b71ca6fed1:/$ cd workspace/cool-app-service-build/app-src/
jenkins@85b71ca6fed1:~/workspace/cool-app-service-build/app-src$ echo "blabla" > docker_coolapp_checksum 
jenkins@85b71ca6fed1:~/workspace/cool-app-service-build/app-src$ exit
```

And now you can rebuild again manually. The build log (on Jenkins), should look something like this:

```text
   .
   .
   .
00:00:01.918 [cool-app-service-build] $ /bin/bash /tmp/jenkins5175889423248321551.sh
00:00:01.920 Checking if any of the Docker configurations changed
00:00:01.920 ========================================
00:00:01.920    Checking BASE Docker configuration
00:00:01.920 ========================================
00:00:01.921    Current BASE file checksum: 3d3234a90b6ce9339e412703a8cf69bfd5a5e3864338e62d481c13fa71233018
00:00:01.921       docker_base_checksum exist
00:00:01.923    Previous BASE file checksum: 3d3234a90b6ce9339e412703a8cf69bfd5a5e3864338e62d481c13fa71233018
00:00:01.923       BUILD_BASE=0
00:00:01.923 ========================================
00:00:01.923    Checking APP build history
00:00:01.923 ========================================
00:00:01.924 removed '/tmp/test.tar.gz'
00:00:01.930    Current BASE file checksum: 3d3234a90b6ce9339e412703a8cf69bfd5a5e3864338e62d481c13fa71233018
00:00:01.930       docker_coolapp_checksum exist
00:00:01.569    Previous APP file checksum: blabla
00:00:01.569       BUILD_BASE=1
00:00:01.747 running sdist
00:00:01.747 running egg_info
00:00:01.749 writing requirements to cool_app.egg-info/requires.txt
   .
   .
   .
00:00:05.663 Successfully built 8388bdde897d
00:00:05.665 Successfully tagged cool-app:44
00:00:05.667       status=0
00:00:05.667       Current working directory: /var/jenkins_home/workspace/cool-app-service-build/app-src
00:00:05.667       COOLAPP build successful
00:00:05.667       Pushing to registry
00:00:05.731 The push refers to repository [192.168.0.160:5000/cool-app]
00:00:05.733 8dc8e52aca9d: Preparing
00:00:05.733 f3cf84baf76f: Preparing
00:00:05.733 92bf97072c74: Preparing
   .
   .
   .
00:00:08.242 dc43d3bc6b5d: Pushed
00:00:09.282 b7f7d2967507: Pushed
00:00:19.601 1dcc1adf1e53: Pushed
00:00:19.641 latest: digest: sha256:971b343e3724020d4401ee219a6f743c1efad51272c7857ff67b312f5a66ab2c size: 3041
00:00:19.650       Successfully pushed to the registry with tag: cool-app:44
00:00:19.650       Local checksum updated
00:00:19.650 
00:00:19.650 
00:00:19.650 ========================================
00:00:19.650 
00:00:19.650 NOTE that at The moment the build needs
00:00:19.650 to be triggered manually and the APP
00:00:19.651 will build every time. Automation is WIP
00:00:19.651 
00:00:19.651 There is a schedule for an hourly build
00:00:19.651 but still no trigger per say.
00:00:19.651 
00:00:19.651 ========================================
00:00:19.696 Finished: SUCCESS
```

## 3.4. Verifying the published image

To verify the image, we must first ensure we remove any local images or left overs from previous build:

```bash
$ docker container ls --all | grep coolapp-rest-service
5624ddf8b499        c39dc72ff2f3                "gunicorn -w 1 -b 0.…"    3 days ago          Exited (0) 3 days ago                                                         coolapp-rest-service
$ docker container rm coolapp-rest-service
coolapp-rest-service
$ docker image ls | grep cool
192.168.0.160:5000/cool-app               latest               8388bdde897d        3 hours ago         524MB
cool-app                                  44                   8388bdde897d        3 hours ago         524MB
cool-app                                  43                   24b6b7ed0f46        3 hours ago         524MB
cool-app                                  42                   cf8b01462082        4 hours ago         524MB
cool-app                                  41                   119907d20c42        4 hours ago         524MB
cool-app                                  40                   db68423347ea        4 hours ago         524MB
cool-app                                  39                   44b8b0c9b0c3        4 hours ago         524MB
cool-app                                  latest               50ae53630d11        4 hours ago         524MB
cool-app-base                             latest               9b76aee0ee2b        23 hours ago        524MB
nicc777/cool-app                          0.0.1                cfd99501514d        6 days ago          494MB
$ docker image rm cool-app
   ...lots of output omitted...
$ for ((i=39;i<=44;i++)); do docker image rm cool-app:$i ; done
   ...lots of output omitted...
$ docker image rm nicc777/cool-app:0.0.1
   ...lots of output omitted...
$ docker image rm 192.168.0.160:5000/cool-app
   ...lots of output omitted...
$ docker image ls | grep cool
cool-app-base                             latest               9b76aee0ee2b        23 hours ago        524MB
```

So now we only have the one in image in the private registry. 

First, ensure it is available by listing the content of the registry:

```bash
curl http://192.168.0.160:5000/v2/_catalog
{"repositories":["cool-app"]}
```

__Note__: If you are using the Enterprise version of Docker, you have the [docker registry](https://docs.docker.com/engine/reference/commandline/registry/) commands to work with in order to inspect and work with remote registries.

Next, try pulling the image (I did this on my `Workstation` to test):

```bash
$ docker pull 192.168.0.160:5000/cool-app 
Using default tag: latest
latest: Pulling from cool-app
23884877105a: Pull complete
bc38caa0f5b9: Pull complete
2910811b6c42: Pull complete
36505266dcc6: Pull complete
77d288724043: Pull complete
da389bcfc808: Pull complete
7d5148397ec6: Pull complete
807b87d8b831: Pull complete
70886ba3ca36: Pull complete
598f21672078: Pull complete
b3dd0509f569: Pull complete
add3ec861ab8: Pull complete
52764cfd15e1: Pull complete
Digest: sha256:971b343e3724020d4401ee219a6f743c1efad51272c7857ff67b312f5a66ab2c
Status: Downloaded newer image for 192.168.0.160:5000/cool-app:latest
192.168.0.160:5000/cool-app:latest
```

# 4. Scenario Discussion

In this scenario we created a private Docker registry and modified our `CI` build to push newly built images to this private registry. All the parts from a `CI` perspective is now in place, **_BUT_** there is still one critical component of `CI` missing and that is around all the unit testing. The application may still have many bugs and without unit tests, there is no way for Jenkins to know if the build will be successful once deployed.

Refer to the [main README](../README.md) in the `master` branch to see which scenarios will cater for Unit Testing (this was not known at the time of completing this piece. FIXME ) 

## 4.1 Trail-Map Progress

| Category                               | Technologies & Patterns Used | Progress and other notes |
|----------------------------------------|------------------------------|--------------------------|
| Containers (Docker)                    | Docker | Current application and database have been containerized |
| CI/CD                                  | Jenkins | The `CI` component now build and pushes an image to a private registry. Still outstanding: unit testing, coverage verification etc. and then the `CD` portion obviously. |
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
| Build, Release, Run           | The `CI` portion of the `CI/CD` pipeline have been implemented with a Jenkins build that will produce an application Docker image on the `Server`. The image is pushed to a Docker registry. |
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

* [Docker documentation on deploying a registry](https://docs.docker.com/registry/deploying/)
* [Docker registry on Docker Hub](https://hub.docker.com/_/registry)