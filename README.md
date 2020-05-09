
- [1. Intro](#1-intro)
- [2. Building](#2-building)
- [3. Start Everything Up from Fresh Builds](#3-start-everything-up-from-fresh-builds)
  - [3.1. The test database server](#31-the-test-database-server)
  - [3.2. Jenkins](#32-jenkins)
- [4. Test](#4-test)
- [5. Setup](#5-setup)
- [6. Conclusion](#6-conclusion)

# 1. Intro

This branch deals with the Jenkins setup up to scenario branch [scenario-200050](https://github.com/nicc777/learning-kubernetes-basics/tree/scenario-200050/scenario)

# 2. Building

Make sure the `jenkins` network is created:

```bash
$ docker network create jenkins
$ docker network ls
NETWORK ID          NAME                DRIVER              SCOPE
60b03c3ac8fc        bridge              bridge              local
eb7762f783b6        coolapp-net         bridge              local
493baa9f41bf        host                host                local
e06038c61d4f        jenkins             bridge              local
8d548a8d6a9c        none                null                local
```

It is assumed the project is built on a `Server` that has Docker running. In my set-up, it is te same server that hosts Minikube, although I am **_not_** installing this Jenkins container in Kubernetes -at least, not yet.

Run:

```bash
$ cd jenkins
$ docker build --no-cache -t jenkins-custom .
```

# 3. Start Everything Up from Fresh Builds

## 3.1. The test database server

The development-testing DB server can be started and prepared as follow (only to be used in later scenarios):

```bash
$ docker container stop jenkins-coolapp-db
jenkins-coolapp-db

$ docker container rm jenkins-coolapp-db
jenkins-coolapp-db

$ docker run --name jenkins-coolapp-db --network=jenkins -p 0.0.0.0:5332:5432 -m 512M --memory-swap 512M --cpu-quota 25000 -e POSTGRES_PASSWORD=mysecretpassword -d postgres
28cc7d0dbb52a91467f709b5d49c8b1dad207125f688725c04c8c81e52ec2865

$ docker run -it --rm --network jenkins postgres psql -h jenkins-coolapp-db -U postgres coolapp
Password for user postgres:
psql: error: could not connect to server: FATAL:  database "coolapp" does not exist

$ docker run -it --rm --network jenkins postgres psql -h jenkins-coolapp-db -U postgres
Password for user postgres:
psql (12.2 (Debian 12.2-2.pgdg100+1))
Type "help" for help.

postgres=# create database coolapp;
CREATE DATABASE
postgres=# \q

$ docker run -it --rm --network jenkins postgres psql -h jenkins-coolapp-db -U postgres coolapp
Password for user postgres:
psql (12.2 (Debian 12.2-2.pgdg100+1))
Type "help" for help.

coolapp=# CREATE TABLE public.user_profiles (
coolapp(#     uid bigserial NOT NULL,
coolapp(#     user_alias varchar(64) NOT NULL,
coolapp(#     user_email_address varchar(255) NOT NULL,
coolapp(#     account_status int4 NOT NULL DEFAULT 1,
coolapp(#     CONSTRAINT user_profiles_pk PRIMARY KEY (uid),
coolapp(#     CONSTRAINT user_profiles_un_001 UNIQUE (user_email_address)
coolapp(# );
CREATE TABLE
coolapp=# CREATE TABLE public.notes (
coolapp(#     nid bigserial NOT NULL,
coolapp(#     uid int4 NOT NULL DEFAULT 1,
coolapp(#     note_timestamp int4 NOT NULL,
coolapp(#     note_text text NOT NULL,
coolapp(#     CONSTRAINT notes_pk PRIMARY KEY (nid),
coolapp(#     CONSTRAINT notes_un_01 UNIQUE (uid, note_timestamp),
coolapp(#     CONSTRAINT notes_un_02 UNIQUE (uid, note_text),
coolapp(#     CONSTRAINT notes_fk FOREIGN KEY (uid) REFERENCES user_profiles(uid) ON UPDATE RESTRICT ON DELETE RESTRICT
coolapp(# );
CREATE TABLE
coolapp=# \d
                  List of relations
 Schema |         Name          |   Type   |  Owner
--------+-----------------------+----------+----------
 public | notes                 | table    | postgres
 public | notes_nid_seq         | sequence | postgres
 public | user_profiles         | table    | postgres
 public | user_profiles_uid_seq | sequence | postgres
(4 rows)

coolapp=# \q
```

## 3.2. Jenkins

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

# 4. Test

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

# 5. Setup

The initial setup of the `Cool App` source will be manual. I hope to use a trigger of sorts at later stage. The configuration does cater for an hourly build though and there are checks to only build hourly if changes in the source was detected.

Changes to the build config may be required as I continue through the scenarios, and as such I have created several job configurations. Below is a table you can use as a guide to choose which version of the configuration to use:

| File version                     | Scenarios                     | Notes |
|----------------------------------|-------------------------------|-------|
| `./jobs/cool-app/config-V1.xml`  | `scenario-200001`             | The basic building of the `cool-app` Docker image. |
| `./jobs/cool-app/config-V2.xml`  | `scenario-200050` | n/a |

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
$ sudo chown <user>:<user> /var/lib/docker/volumes/jenkins-data/_data/jobs/cool-app-service-build
$ sudo chown <user>:<user> /var/lib/docker/volumes/jenkins-data/_data/jobs/cool-app-service-build/config.xml
```

Now, restart Jenkins:

```bash
$ docker container restart jenkins-coolapp-builder
```

# 6. Conclusion

The `CI` portion is now complete. 
