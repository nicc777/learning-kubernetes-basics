
- [1. Intro](#1-intro)
- [2. Building & Testing](#2-building--testing)
- [3. Adding the new build pipeline](#3-adding-the-new-build-pipeline)
  - [3.1. Prepare the jobs](#31-prepare-the-jobs)
- [5. Docker Registry Discussion](#5-docker-registry-discussion)
  - [5.1. List all the images:](#51-list-all-the-images)
  - [5.2. Get the tags for a particular image:](#52-get-the-tags-for-a-particular-image)
  - [5.3. Cleanup some old images tags](#53-cleanup-some-old-images-tags)
- [6. Running the builds on Jenkins](#6-running-the-builds-on-jenkins)
- [7. Creating a Jenkins Pipeline](#7-creating-a-jenkins-pipeline)
- [8. Special note on the `coolapp-coverage` Job - Parameterized Builds](#8-special-note-on-the-coolapp-coverage-job---parameterized-builds)

# 1. Intro

This branch set-up the build pipeline for the [`appsrc-0.0.2`](https://github.com/nicc777/learning-kubernetes-basics/tree/appsrc-0.0.2/app-src) code branch.

# 2. Building & Testing

If you have followed the previous scenarios, you would not need to build Jenkins again. Just make sure it is running.I

If you need to build Jenkins, please checkout branch [`jenkins-upto-scenario-200050`](https://github.com/nicc777/learning-kubernetes-basics/tree/jenkins-upto-scenario-200050) and run through the README

__Important__: Ensure that any schedules or triggers currently defined in Jenkins is disabled or deleted.

# 3. Adding the new build pipeline

__Important__: Ensure you are in the base directory of the project:

```bash
$ cd $TUTORIAL_HOME
```

## 3.1. Prepare the jobs

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

Next, run the following:

```bash
$ sudo mkdir /var/lib/docker/volumes/jenkins-data/_data/jobs/{coolapp-src-build,coolapp-service-image-build,coolapp-coverage,coolapp-base-docker-image-build}

$ sudo cp -vf jenkins/jobs/coolapp-src-build/config.xml /var/lib/docker/volumes/jenkins-data/_data/jobs/coolapp-src-build/

$ sudo cp -vf jenkins/jobs/coolapp-base-docker-image-build/config.xml /var/lib/docker/volumes/jenkins-data/_data/jobs/coolapp-base-docker-image-build/

$ sudo cp -vf jenkins/jobs/coolapp-coverage/config.xml /var/lib/docker/volumes/jenkins-data/_data/jobs/coolapp-coverage/

$ sudo cp -vf jenkins/jobs/coolapp-service-image-build/config.xml /var/lib/docker/volumes/jenkins-data/_data/jobs/coolapp-service-image-build/

$ sudo find /var/lib/docker/volumes/jenkins-data/_data/jobs/ -type d -iname coolapp* -exec chown -R <user>.<user> {} \;
```

__Note__: Typically the Jenkins `../jobs` directory will not be owned by `root`. Make sure that the `../jobs/config.xml` file is also owned by the same user as `../jobs`.

And now restart Jenkins again:

```bash
$ docker container restart jenkins-coolapp-builder
```

# 5. Docker Registry Discussion

The private registry exposes and API, [which is well documented](https://docs.docker.com/registry/spec/api/)

__NOTE__: In order to ENABLE deletion from the registry, you have to start it with the `-e REGISTRY_STORAGE_DELETE_ENABLED=true` parameter.

__Important__: I had to experiment with several options to enable deletion of images on the registry. It seems that the parameter name tends to have changed over time, so there are more than one option. The one listed here was accurate as of 10 May 2020. 

## 5.1. List all the images:

```bash
$ curl http://127.0.0.1:5000/v2/_catalog
{"repositories":["cool-app","cool-app-base"]}
```

## 5.2. Get the tags for a particular image:

In the following example, I want to delete the older image tag nr 11

```bash
$ curl http://127.0.0.1:5000/v2/cool-app-base/tags/list
{"name":"cool-app-base","tags":["12","11"]}

$ curl -v -X GET -H "Accept: application/vnd.docker.distribution.manifest.v2+json" http://127.0.0.1:5000/v2/cool-app-base/manifests/11
Note: Unnecessary use of -X or --request, GET is already inferred.
*   Trying 127.0.0.1...
* TCP_NODELAY set
* Connected to 127.0.0.1 (127.0.0.1) port 5000 (#0)
> GET /v2/cool-app-base/manifests/11 HTTP/1.1
> Host: 127.0.0.1:5000
> User-Agent: curl/7.58.0
> Accept: application/vnd.docker.distribution.manifest.v2+json
>
< HTTP/1.1 200 OK
< Content-Length: 2001
< Content-Type: application/vnd.docker.distribution.manifest.v2+json
< Docker-Content-Digest: sha256:0e0b02121cffdc04008f1b1e389f5785b3bb1a91eda50d413ab9b284acc30e4b
< Docker-Distribution-Api-Version: registry/2.0
< Etag: "sha256:0e0b02121cffdc04008f1b1e389f5785b3bb1a91eda50d413ab9b284acc30e4b"
< X-Content-Type-Options: nosniff
< Date: Sun, 10 May 2020 08:41:41 GMT
<
{
   "schemaVersion": 2,
   "mediaType": "application/vnd.docker.distribution.manifest.v2+json",
   "config": {
      "mediaType": "application/vnd.docker.container.image.v1+json",
      "size": 5126,
      "digest": "sha256:2896539299c18137c773a754ada174db12935a3803d89975d161d39a8558d9d9"
   },
   "layers": [
   .
   .
   .
   ]
* Connection #0 to host 127.0.0.1 left intact
```

__Note__: The image tag checksum is listed in the header `Docker-Content-Digest`

## 5.3. Cleanup some old images tags

Using the `Docker-Content-Digest` value from the previous command, run the following:

```bash
curl -v -X DELETE http://127.0.0.1:5000/v2/cool-app-base/manifests/sha256:0e0b02121cffdc04008f1b1e389f5785b3bb1a91eda50d413ab9b284acc30e4b
*   Trying 127.0.0.1...
* TCP_NODELAY set
* Connected to 127.0.0.1 (127.0.0.1) port 5000 (#0)
> DELETE /v2/cool-app-base/manifests/sha256:0e0b02121cffdc04008f1b1e389f5785b3bb1a91eda50d413ab9b284acc30e4b HTTP/1.1
> Host: 127.0.0.1:5000
> User-Agent: curl/7.58.0
> Accept: */*
>
< HTTP/1.1 202 Accepted
< Docker-Distribution-Api-Version: registry/2.0
< X-Content-Type-Options: nosniff
< Date: Sun, 10 May 2020 08:49:22 GMT
< Content-Length: 0
<
* Connection #0 to host 127.0.0.1 left intact
```

Verify:

```bash
$ curl http://127.0.0.1:5000/v2/cool-app-base/tags/list
{"name":"cool-app-base","tags":["12"]}
```

# 6. Running the builds on Jenkins

The first manual run should be done in the following order:

* `coolapp-base-docker-image-build`
* `coolapp-coverage`
* `coolapp-src-build`
* `coolapp-service-image-build`

# 7. Creating a Jenkins Pipeline

As with any other Jenkins Job, copy the config and restart:

```bash
$ sudo mkdir /var/lib/docker/volumes/jenkins-data/_data/jobs/coolapp-pipeline

$ sudo cp -vf jenkins/jobs/coolapp-pipeline/config.xml /var/lib/docker/volumes/jenkins-data/_data/jobs/coolapp-pipeline/
```

__Note__: Typically the Jenkins `../jobs` directory will not be owned by `root`. Make sure that the `../jobs/config.xml` file is also owned by the same user as `../jobs`.

And now restart Jenkins again:

```bash
$ docker container restart jenkins-coolapp-builder
```

# 8. Special note on the `coolapp-coverage` Job - Parameterized Builds

This job uses a parameter, [configured as per documentation](https://wiki.jenkins.io/display/JENKINS/Parameterized+Build), to set the coverage level.

When the build is manually run, you will have the opportunity to adjust the level. To permanently set a new default level, you have to configure the Job in Jenkins.

__Note__: Pipeline builds will use the default value and will not provide you an option to set the value.
