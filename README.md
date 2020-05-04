
- [1. Building](#1-building)
- [2. Start](#2-start)
- [3. Test](#3-test)
- [4. Setup](#4-setup)

# 1. Building

Run:

```bash
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

# 3. Test

TODO

# 4. Setup

TODO
