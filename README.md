
- [1. Building](#1-building)
- [2. Start](#2-start)
- [3. Test](#3-test)
- [4. Setup](#4-setup)

# 1. Building

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

TODO

1. Get the volume config (path)
1. Copy the config.xml file to a new job

The following is run from the `Server`:

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

Now, create a JOB:

```bash
$ sudo mkdir /var/lib/docker/volumes/jenkins-data/_data/jobs/test-docker-access
$ sudo cp -vf ./config.xml /var/lib/docker/volumes/jenkins-data/_data/jobs/test-docker-access
```

__Note__: Typically the `../jobs` directory will not be owned by `root`. Make sure that the `../jobs/config.xml` file is also owned by the same user as `../jobs`.

```bash
$ sudo chown <user>:<user> /var/lib/docker/volumes/jenkins-data/_data/jobs/test-docker-access
$ sudo chown <user>:<user> /var/lib/docker/volumes/jenkins-data/_data/jobs/test-docker-access/config.xml
```

Now, restart Jenkins:

```bash
$ docker container restart jenkins-coolapp-builder
```

Run the new job from the browser console. If all worked out well, you should be able to see the two files created in the job `Workspace`:

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

If the file exists and you see output, then everything is ready for setting up the final build job.

# 4. Setup

TODO
