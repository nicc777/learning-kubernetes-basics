
- [1. Intro](#1-intro)
- [2. Building](#2-building)
- [3. Adding the new build pipeline](#3-adding-the-new-build-pipeline)
- [5. Setup](#5-setup)
- [6. Conclusion](#6-conclusion)

# 1. Intro

This branch set-up the build pipeline for the [`appsrc-0.0.2`](https://github.com/nicc777/learning-kubernetes-basics/tree/appsrc-0.0.2/app-src) code branch.

# 2. Building

If you have followed the previous scenarios, you would not need to build Jenkins again. Just make sure it is running.I

If you need to build Jenkins, please checkout branch [`jenkins-upto-scenario-200050`](https://github.com/nicc777/learning-kubernetes-basics/tree/jenkins-upto-scenario-200050) and run through the README

To ensure Jenkins is running:

```bash
$ docker container ls | grep -v k8s
CONTAINER ID        IMAGE               COMMAND                  CREATED             STATUS              PORTS                                              NAMES
abd1bed6bc30        registry:2          "/entrypoint.sh /etc…"   2 days ago          Up 2 hours          0.0.0.0:5000->5000/tcp                             registry
85b71ca6fed1        jenkins-custom      "/sbin/tini -- /usr/…"   4 days ago          Up 2 hours          0.0.0.0:50000->50000/tcp, 0.0.0.0:8085->8080/tcp   jenkins-coolapp-builder
b6acbb212160        postgres            "docker-entrypoint.s…"   8 days ago          Up 2 hours          127.0.0.1:5432->5432/tcp                           coolapp-db
```

For the build to be done, both `jenkins-coolapp-db` and `jenkins-coolapp-builder` must be running.

To start either or both of these, run:

```bash
$ docker container start coolapp-db
$ docker container start jenkins-coolapp-builder
```

TODO:
```text
$ pwd
/var/jenkins_home/workspace/coolapp-base-docker-image-build
jenkins@85b71ca6fed1:~/workspace/coolapp-base-docker-image-build$ echo $HOME
/var/jenkins_home

________________

$ cd
jenkins@85b71ca6fed1:~$ cd workspace/coolapp-src-build/
jenkins@85b71ca6fed1:~/workspace/coolapp-src-build$ cd app-src/dist/
jenkins@85b71ca6fed1:~/workspace/coolapp-src-build/app-src/dist$ pwd
/var/jenkins_home/workspace/coolapp-src-build/app-src/dist
jenkins@85b71ca6fed1:~/workspace/coolapp-src-build/app-src/dist$ ls
cool_app-0.0.2.tar.gz

____________________

docker run --name jenkins-coolapp-db \
--network=jenkins \
-p 0.0.0.0:5332:5432 \
-m 512M --memory-swap 512M \
--cpu-quota 25000 \
-e POSTGRES_PASSWORD=mysecretpassword \
-d postgres
```

# 3. Adding the new build pipeline

The following is run from the `Server`, and will determine exactly where the Jenkins volume's files live:

```bash
$ docker volume inspect jenkins-data
[
    {
        "CreatedAt": "2020-05-05T09:11:09+02:00",
        "Driver": "local",
        "Labels": {},
        "Mountpoint": "/var/lib/docker/volumes/jenkins-data/_data",
        "Name": "jenkins-data",
        "Options": {},
        "Scope": "local"
    }
]
```

Take note of the `Mountpoint`.

Next, copy the TEST job from this project:

```bash
$ sudo mkdir /var/lib/docker/volumes/jenkins-data/_data/jobs/test-docker-access
$ sudo cp -vf ./jobs/test/config.xml /var/lib/docker/volumes/jenkins-data/_data/jobs/test-docker-access
```

__Note__: Typically the Jenkins `../jobs` directory will not be owned by `root`. Make sure that the `../jobs/config.xml` file is also owned by the same user as `../jobs`.

```bash
$ sudo chown <user>:<user> /var/lib/docker/volumes/jenkins-data/_data/jobs/test-docker-access
$ sudo chown <user>:<user> /var/lib/docker/volumes/jenkins-data/_data/jobs/test-docker-access/config.xml
```

Now, restart Jenkins:

```bash
$ docker container restart jenkins-coolapp-builder
```

Run a build from the new job from the Jenkins browser console. If all worked out well, you should be able to see the two files created in the job `Workspace`:

```bash
$ sudo ls -lahrt /var/lib/docker/volumes/jenkins-data/_data/workspace/test-docker-access
total 20K
-rw-r--r-- 1 user user 6.2K May  5 08:50 containers.txt
drwxr-xr-x 2 user user 4.0K May  5 08:50 .
-rw-r--r-- 1 user user  396 May  5 08:50 networks.txt
drwxr-xr-x 4 user user 4.0K May  5 09:10 ..
$ sudo cat /var/lib/docker/volumes/jenkins-data/_data/workspace/test-docker-access/networks.txt
NETWORK ID          NAME                DRIVER              SCOPE
dcd059f0977e        bridge              bridge              local
eb7762f783b6        coolapp-net         bridge              local
493baa9f41bf        host                host                local
e06038c61d4f        jenkins             bridge              local
8d548a8d6a9c        none                null                local
```

If the files exists and you see output, then everything is ready for setting up the final build job.

# 5. Setup

The initial setup of the `Cool App` source will be manual. I hope to use a trigger of sorts at later stage. The configuration does cater for an hourly build though and there are checks to only build hourly if changes in the source was detected.

Changes to the build config may be required as I continue through the scenarios, and as such I have created several job configurations. Below is a table you can use as a guide to choose which version of the configuration to use:

| File version                     | Scenarios                     | Notes |
|----------------------------------|-------------------------------|-------|
| `./jobs/cool-app/config-V1.xml`  | `scenario-200001`             | The basic building of the `cool-app` Docker image. |
| `./jobs/cool-app/config-V2.xml`  | From `scenario-200050` onward | This will be updated as soon a V3 is created. In the `config-V2.xml`, be sure to set your registry host details |

__Important__: The configurations will all point to the [original repo](https://github.com/nicc777/learning-kubernetes-basics). If you want to point to your own fork, search for the following in the config and update the URL to point to your repo:

```xml
    <userRemoteConfigs>
      <hudson.plugins.git.UserRemoteConfig>
        <name>coolapp-origin</name>
        <url>https://github.com/nicc777/learning-kubernetes-basics</url>
      </hudson.plugins.git.UserRemoteConfig>
    </userRemoteConfigs>
```

Still using the `Mountpoint` from the previous section, follow this process.

Copy the `cool app` job from to the Jenkins jobs:

```bash
$ sudo mkdir /var/lib/docker/volumes/jenkins-data/_data/jobs/cool-app-service-build
$ sudo cp -vf ./jobs/cool-app/config-V1.xml /var/lib/docker/volumes/jenkins-data/_data/jobs/cool-app-service-build/config.xml
```

__Note__: Typically the Jenkins `../jobs` directory will not be owned by `root`. Make sure that the `../jobs/config.xml` file is also owned by the same user as `../jobs`.

```bash
$ sudo chown <user>:<user> /var/lib/docker/volumes/jenkins-data/_data/jobs/test-docker-access
$ sudo chown <user>:<user> /var/lib/docker/volumes/jenkins-data/_data/jobs/test-docker-access/config.xml
```

Now, restart Jenkins:

```bash
$ docker container restart jenkins-coolapp-builder
```

# 6. Conclusion

The `CI` portion is now complete. 
