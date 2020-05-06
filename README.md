
- [1. Building](#1-building)
- [2. Start](#2-start)
- [3. Test](#3-test)
- [4. Setup](#4-setup)
- [5. Conclusion](#5-conclusion)

# 1. Building

It is assumed the project is built on a `Server` that has Docker running. In my set-up, it is te same server that hosts Minikube, although I am **_not_** installing this Jenkins container in Kubernetes -at least, not yet.

Run:

```bash
$ cd jenkins
$ docker build --no-cache -t jenkins-custom .
```

# 2. Start

Run:

```bash
$ docker container run \
--name jenkins-coolapp-builder \
-d \
--network jenkins \
-p 0.0.0.0:8085:8080 \
-p 0.0.0.0:50000:50000 \
-v jenkins-data:/var/jenkins_home \
-v /var/run/docker.sock:/var/run/docker.sock \
jenkins-custom
```

You will have to tail the log file in order to find the password:

```bash
$ docker logs -f jenkins-coolapp-builder
Running from: /usr/share/jenkins/jenkins.war
webroot: EnvVars.masterEnvVars.get("JENKINS_HOME")
2020-05-05 06:37:31.685+0000 [id=1]     INFO    org.eclipse.jetty.util.log.Log#initialized: Logging initialized @297ms to org.eclipse.jetty.util.log.JavaUtilLog
   .
   .
   .
2020-05-05 06:37:37.255+0000 [id=30]    INFO    jenkins.install.SetupWizard#init: 

*************************************************************
*************************************************************
*************************************************************

Jenkins initial setup is required. An admin user has been created and a password generated.
Please use the following password to proceed to installation:

a3d8da6daa46442b951761b47f2d9e1e

This may also be found at: /var/jenkins_home/secrets/initialAdminPassword

*************************************************************
*************************************************************
*************************************************************
```

Once you see the password, you can launch your web browser and navigate to the Jenkins home page. On my system that would be http://192.168.0.160:8085/

You can select to install all the suggested plugins - for this project that will be all that is required.

This process takes a couple of minutes.

# 3. Test

Of critical importance is to test if the Jenkins container can communicate with the Docker daemon running on the host `Server`, which is exposed via Unix sockets.

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

# 4. Setup

The initial setup of the `Cool App` source will be manual. I hope to use a trigger of sorts at later stage. The configuration does cater for an hourly build though and there are checks to only build hourly if changes in the source was detected.

Changes to the build config may be required as I continue through the scenarios, and as such I have created several job configurations. Below is a table you can use as a guide to choose which version of the configuration to use:

| File version                     | Scenarios                 | Notes |
|----------------------------------|---------------------------|-------|
| `./jobs/cool-app/config-V1.xml`  | All the initial scenarios | This will be updated as soon a V2 is created |

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

# 5. Conclusion

The `CI` portion is now complete. 
