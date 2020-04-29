
- [1. Editing number of replicas in a running cluster](#1-editing-number-of-replicas-in-a-running-cluster)
- [2. Resurrecting the dead](#2-resurrecting-the-dead)
- [3. View POD log files](#3-view-pod-log-files)
- [4. Getting inside a POD's head](#4-getting-inside-a-pods-head)
  - [4.1 Access a shell in a running POD](#41-access-a-shell-in-a-running-pod)
  - [4.2 Executing a command in a running POD](#42-executing-a-command-in-a-running-pod)

# 1. Editing number of replicas in a running cluster

Assuming you have [version 0.0.1](../kubernetes/cool-app-0.0.1.yml) of the app running, you will notice in that configuration that the number of replicas is set to 1:

```yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cool-app-deployment
  labels:
    app: cool-app
spec:
  replicas: 1
```

In a running deployment you can edit the configuration by issuing the following command that will open the running configuration in an editor (default may be `vi` or `vim`, depending on how your system is configured):

```bash
$ kubectl edit deployment.v1.apps/cool-app-deployment
```

The opened configuration looks very similar to the original file. Search for `replicas` and change the `1` to `2` and save+exit the editor (`:wq` in `vim`).

You will now have 2 running pods:

```bash
$ kubectl get pods
NAME                                   READY   STATUS    RESTARTS   AGE
cool-app-deployment-7df4f7dbfd-5tmw6   1/1     Running   0          11s
cool-app-deployment-7df4f7dbfd-v4vmt   1/1     Running   0          8m35s
```

If you had a running `while true; do curl http://$IP:$PORT/status; sleep .3; done` command in a separate window, you may have noticed the following:

```text
pid=31   |   hostname=cool-app-deployment-7df4f7dbfd-v4vmt     |   app_version=0.0.1   |   uptime=387
pid=35   |   hostname=cool-app-deployment-7df4f7dbfd-v4vmt     |   app_version=0.0.1   |   uptime=386
pid=31   |   hostname=cool-app-deployment-7df4f7dbfd-v4vmt     |   app_version=0.0.1   |   uptime=388
pid=31   |   hostname=cool-app-deployment-7df4f7dbfd-v4vmt     |   app_version=0.0.1   |   uptime=388
pid=37   |   hostname=cool-app-deployment-7df4f7dbfd-v4vmt     |   app_version=0.0.1   |   uptime=385
pid=33   |   hostname=cool-app-deployment-7df4f7dbfd-v4vmt     |   app_version=0.0.1   |   uptime=388
pid=33   |   hostname=cool-app-deployment-7df4f7dbfd-v4vmt     |   app_version=0.0.1   |   uptime=388
pid=33   |   hostname=cool-app-deployment-7df4f7dbfd-v4vmt     |   app_version=0.0.1   |   uptime=389
pid=37   |   hostname=cool-app-deployment-7df4f7dbfd-v4vmt     |   app_version=0.0.1   |   uptime=386
pid=14   |   hostname=cool-app-deployment-7df4f7dbfd-5tmw6     |   app_version=0.0.1   |   uptime=8
pid=14   |   hostname=cool-app-deployment-7df4f7dbfd-5tmw6     |   app_version=0.0.1   |   uptime=9
pid=14   |   hostname=cool-app-deployment-7df4f7dbfd-5tmw6     |   app_version=0.0.1   |   uptime=9
pid=37   |   hostname=cool-app-deployment-7df4f7dbfd-v4vmt     |   app_version=0.0.1   |   uptime=387
pid=14   |   hostname=cool-app-deployment-7df4f7dbfd-5tmw6     |   app_version=0.0.1   |   uptime=10
pid=37   |   hostname=cool-app-deployment-7df4f7dbfd-v4vmt     |   app_version=0.0.1   |   uptime=388
pid=14   |   hostname=cool-app-deployment-7df4f7dbfd-5tmw6     |   app_version=0.0.1   |   uptime=10
pid=35   |   hostname=cool-app-deployment-7df4f7dbfd-v4vmt     |   app_version=0.0.1   |   uptime=391
pid=35   |   hostname=cool-app-deployment-7df4f7dbfd-v4vmt     |   app_version=0.0.1   |   uptime=391
pid=14   |   hostname=cool-app-deployment-7df4f7dbfd-5tmw6     |   app_version=0.0.1   |   uptime=11
pid=37   |   hostname=cool-app-deployment-7df4f7dbfd-v4vmt     |   app_version=0.0.1   |   uptime=389
```

The load balancer starts to send requests to the new POD, which now responds with a much lower `uptime` than the old running POD.

# 2. Resurrecting the dead

If a POD dies, it will automatically restart. Let's test that.

You will need a running version of [version 0.0.1](../kubernetes/cool-app-0.0.1.yml) of the cool app.

In a terminal window set a watch with the following command: `watch -n 2 kubectl get pods --show-labels`. You will see something like this:

```text
Every 2.0s: kubectl get pods --show-labels                                                                                                                                    ng3: Wed Apr 29 06:44:43 2020
NAME                                   READY   STATUS    RESTARTS   AGE    LABELS
cool-app-deployment-7df4f7dbfd-cqlfd   1/1     Running   0          5m2s   app=cool-app,pod-template-hash=7df4f7dbfd
cool-app-deployment-7df4f7dbfd-g226k   1/1     Running   0          4m8s   app=cool-app,pod-template-hash=7df4f7dbfd
```

In a second terminal window run `while true; do curl http://$IP:$PORT/status; sleep .3; done`.

Now run the following command in a third terminal and watch what happens in the other terminal windows:

```bash
$ curl http://$IP:$PORT/die
```

Snapshot 1:

```text
Every 2.0s: kubectl get pods --show-labels                                                                                                                                     ng3: Wed Apr 29 06:48:28 2020

NAME                                   READY   STATUS    RESTARTS   AGE     LABELS
cool-app-deployment-7df4f7dbfd-cqlfd   1/1     Running   0          8m47s   app=cool-app,pod-template-hash=7df4f7dbfd
cool-app-deployment-7df4f7dbfd-g226k   0/1     Running   1          7m53s   app=cool-app,pod-template-hash=7df4f7dbfd
```

Snapshot 2:

```text
Every 2.0s: kubectl get pods --show-labels                                                                                                                                     ng3: Wed Apr 29 06:48:36 2020

NAME                                   READY   STATUS    RESTARTS   AGE     LABELS
cool-app-deployment-7df4f7dbfd-cqlfd   1/1     Running   0          8m56s   app=cool-app,pod-template-hash=7df4f7dbfd
cool-app-deployment-7df4f7dbfd-g226k   1/1     Running   1          8m2s    app=cool-app,pod-template-hash=7df4f7dbfd
```

Snapshot 3:

```text
pid=8    |   hostname=cool-app-deployment-7df4f7dbfd-g226k     |   app_version=0.0.1   |   uptime=462
pid=11   |   hostname=cool-app-deployment-7df4f7dbfd-cqlfd     |   app_version=0.0.1   |   uptime=516
pid=8    |   hostname=cool-app-deployment-7df4f7dbfd-g226k     |   app_version=0.0.1   |   uptime=463
pid=12   |   hostname=cool-app-deployment-7df4f7dbfd-g226k     |   app_version=0.0.1   |   uptime=463
pid=12   |   hostname=cool-app-deployment-7df4f7dbfd-g226k     |   app_version=0.0.1   |   uptime=463
pid=9    |   hostname=cool-app-deployment-7df4f7dbfd-cqlfd     |   app_version=0.0.1   |   uptime=518
pid=12   |   hostname=cool-app-deployment-7df4f7dbfd-g226k     |   app_version=0.0.1   |   uptime=464
pid=12   |   hostname=cool-app-deployment-7df4f7dbfd-g226k     |   app_version=0.0.1   |   uptime=464
pid=14   |   hostname=cool-app-deployment-7df4f7dbfd-cqlfd     |   app_version=0.0.1   |   uptime=517
pid=14   |   hostname=cool-app-deployment-7df4f7dbfd-g226k     |   app_version=0.0.1   |   uptime=465
pid=8    |   hostname=cool-app-deployment-7df4f7dbfd-g226k     |   app_version=0.0.1   |   uptime=465
pid=14   |   hostname=cool-app-deployment-7df4f7dbfd-g226k     |   app_version=0.0.1   |   uptime=465
pid=11   |   hostname=cool-app-deployment-7df4f7dbfd-cqlfd     |   app_version=0.0.1   |   uptime=520
pid=10   |   hostname=cool-app-deployment-7df4f7dbfd-g226k     |   app_version=0.0.1   |   uptime=466
pid=12   |   hostname=cool-app-deployment-7df4f7dbfd-cqlfd     |   app_version=0.0.1   |   uptime=519
pid=10   |   hostname=cool-app-deployment-7df4f7dbfd-g226k     |   app_version=0.0.1   |   uptime=467
pid=10   |   hostname=cool-app-deployment-7df4f7dbfd-g226k     |   app_version=0.0.1   |   uptime=467
pid=10   |   hostname=cool-app-deployment-7df4f7dbfd-g226k     |   app_version=0.0.1   |   uptime=467
pid=10   |   hostname=cool-app-deployment-7df4f7dbfd-g226k     |   app_version=0.0.1   |   uptime=468
pid=11   |   hostname=cool-app-deployment-7df4f7dbfd-cqlfd     |   app_version=0.0.1   |   uptime=522
pid=12   |   hostname=cool-app-deployment-7df4f7dbfd-cqlfd     |   app_version=0.0.1   |   uptime=521
pid=12   |   hostname=cool-app-deployment-7df4f7dbfd-cqlfd     |   app_version=0.0.1   |   uptime=522
pid=9    |   hostname=cool-app-deployment-7df4f7dbfd-g226k     |   app_version=0.0.1   |   uptime=1
pid=9    |   hostname=cool-app-deployment-7df4f7dbfd-cqlfd     |   app_version=0.0.1   |   uptime=523
pid=11   |   hostname=cool-app-deployment-7df4f7dbfd-cqlfd     |   app_version=0.0.1   |   uptime=524
pid=11   |   hostname=cool-app-deployment-7df4f7dbfd-cqlfd     |   app_version=0.0.1   |   uptime=524
pid=9    |   hostname=cool-app-deployment-7df4f7dbfd-cqlfd     |   app_version=0.0.1   |   uptime=524
pid=12   |   hostname=cool-app-deployment-7df4f7dbfd-cqlfd     |   app_version=0.0.1   |   uptime=523
pid=9    |   hostname=cool-app-deployment-7df4f7dbfd-cqlfd     |   app_version=0.0.1   |   uptime=525
pid=12   |   hostname=cool-app-deployment-7df4f7dbfd-cqlfd     |   app_version=0.0.1   |   uptime=524
pid=12   |   hostname=cool-app-deployment-7df4f7dbfd-cqlfd     |   app_version=0.0.1   |   uptime=524
pid=11   |   hostname=cool-app-deployment-7df4f7dbfd-cqlfd     |   app_version=0.0.1   |   uptime=526
pid=12   |   hostname=cool-app-deployment-7df4f7dbfd-cqlfd     |   app_version=0.0.1   |   uptime=525
pid=12   |   hostname=cool-app-deployment-7df4f7dbfd-cqlfd     |   app_version=0.0.1   |   uptime=525
pid=12   |   hostname=cool-app-deployment-7df4f7dbfd-cqlfd     |   app_version=0.0.1   |   uptime=526
pid=11   |   hostname=cool-app-deployment-7df4f7dbfd-cqlfd     |   app_version=0.0.1   |   uptime=527
pid=11   |   hostname=cool-app-deployment-7df4f7dbfd-cqlfd     |   app_version=0.0.1   |   uptime=527
pid=11   |   hostname=cool-app-deployment-7df4f7dbfd-cqlfd     |   app_version=0.0.1   |   uptime=528
pid=9    |   hostname=cool-app-deployment-7df4f7dbfd-g226k     |   app_version=0.0.1   |   uptime=6
pid=11   |   hostname=cool-app-deployment-7df4f7dbfd-g226k     |   app_version=0.0.1   |   uptime=5
pid=14   |   hostname=cool-app-deployment-7df4f7dbfd-cqlfd     |   app_version=0.0.1   |   uptime=528
pid=9    |   hostname=cool-app-deployment-7df4f7dbfd-g226k     |   app_version=0.0.1   |   uptime=7
pid=10   |   hostname=cool-app-deployment-7df4f7dbfd-g226k     |   app_version=0.0.1   |   uptime=6
pid=14   |   hostname=cool-app-deployment-7df4f7dbfd-cqlfd     |   app_version=0.0.1   |   uptime=529
```

Notice how the `READY` indicator for one POD changed to `0/1` and how it was then restarted. The restart is also incremented that POD's `RESTART` counter to `1`.

The service was recovered uninterrupted since there were enough POD's running to continue serve all requests. As the one POD was restarted, for a time all requests were handled by the remaining running POD.

To examine the detailed POD description, run the following:

```bash
$ kubectl describe pod cool-app-deployment-7df4f7dbfd-g226k
Name:         cool-app-deployment-7df4f7dbfd-g226k
Namespace:    demo
Priority:     0
Node:         ng3/192.168.0.160
Start Time:   Wed, 29 Apr 2020 06:40:35 +0200
Labels:       app=cool-app
              pod-template-hash=7df4f7dbfd
Annotations:  <none>
Status:       Running
IP:           172.17.0.9
IPs:
  IP:           172.17.0.9
Controlled By:  ReplicaSet/cool-app-deployment-7df4f7dbfd
Containers:
  cool-app:
    Container ID:   docker://83478dfc743b44b93a30832d2ed5748d35914fde06384cc0fcf748d523aa057c
    Image:          nicc777/cool-app:0.0.1
    Image ID:       docker-pullable://nicc777/cool-app@sha256:b2f26a7dfb2cef4f05d1fc2c5a9f4a3a69a15443070bbb57b0b76ced6fa7a0be
    Port:           8080/TCP
    Host Port:      0/TCP
    State:          Running
      Started:      Wed, 29 Apr 2020 06:48:24 +0200
    Last State:     Terminated
      Reason:       Completed
      Exit Code:    0
      Started:      Wed, 29 Apr 2020 06:40:36 +0200
      Finished:     Wed, 29 Apr 2020 06:48:24 +0200
    Ready:          True
    Restart Count:  1
    Limits:
      cpu:     1
      memory:  256Mi
    Requests:
      cpu:        500m
      memory:     256Mi
    Liveness:     http-get http://:8080/probe/alive delay=3s timeout=1s period=3s #success=1 #failure=3
    Readiness:    http-get http://:8080/probe/ready delay=5s timeout=1s period=5s #success=1 #failure=3
    Environment:  <none>
    Mounts:
      /var/run/secrets/kubernetes.io/serviceaccount from default-token-kgs6c (ro)
Conditions:
  Type              Status
  Initialized       True 
  Ready             True 
  ContainersReady   True 
  PodScheduled      True 
Volumes:
  default-token-kgs6c:
    Type:        Secret (a volume populated by a Secret)
    SecretName:  default-token-kgs6c
    Optional:    false
QoS Class:       Burstable
Node-Selectors:  <none>
Tolerations:     node.kubernetes.io/not-ready:NoExecute for 300s
                 node.kubernetes.io/unreachable:NoExecute for 300s
Events:
  Type     Reason     Age                From               Message
  ----     ------     ----               ----               -------
  Normal   Scheduled  <unknown>          default-scheduler  Successfully assigned demo/cool-app-deployment-7df4f7dbfd-g226k to ng3
  Normal   Pulled     21m (x2 over 29m)  kubelet, ng3       Container image "nicc777/cool-app:0.0.1" already present on machine
  Normal   Created    21m (x2 over 29m)  kubelet, ng3       Created container cool-app
  Normal   Started    21m (x2 over 29m)  kubelet, ng3       Started container cool-app
  Warning  Unhealthy  21m (x3 over 21m)  kubelet, ng3       Liveness probe failed: HTTP probe failed with statuscode: 500
  Normal   Killing    21m                kubelet, ng3       Container cool-app failed liveness probe, will be restarted
```

Note the `Events` toward the end.

# 3. View POD log files

List the pods:

```bash
$ kubectl get pods --show-labels
NAME                                   READY   STATUS    RESTARTS   AGE   LABELS
cool-app-deployment-7df4f7dbfd-cqlfd   1/1     Running   0          41m   app=cool-app,pod-template-hash=7df4f7dbfd
cool-app-deployment-7df4f7dbfd-g226k   1/1     Running   1          41m   app=cool-app,pod-template-hash=7df4f7dbfd
```

Get the logs of a POD:

```bash
$ kubectl logs cool-app-deployment-7df4f7dbfd-g226k | less
```

To exclude the probes:

```bash
$ kubectl logs cool-app-deployment-7df4f7dbfd-g226k | grep -v "/probe/" | less
```

__Note__: Since the POD was restarted, you will NOT find the request to the `/die` resource (see [2. Resurrecting the dead](#2-resurrecting-the-dead)). Logs are not persisted between restarts.

Consider also the following tools for log viewing/tailing:

* [kail](https://github.com/boz/kail)
* [stern](https://github.com/wercker/stern)

# 4. Getting inside a POD's head

If there are some rare case when a POD needs to be accessed directly, the following commands could help:

## 4.1 Access a shell in a running POD

```bash
$ kubectl exec -it cool-app-deployment-7df4f7dbfd-cqlfd /bin/bash
root@cool-app-deployment-7df4f7dbfd-cqlfd:/usr/src/app# cat /etc/os-release 
NAME="Ubuntu"
VERSION="18.04.4 LTS (Bionic Beaver)"
ID=ubuntu
ID_LIKE=debian
PRETTY_NAME="Ubuntu 18.04.4 LTS"
VERSION_ID="18.04"
...
```

## 4.2 Executing a command in a running POD

```bash
$ kubectl exec cool-app-deployment-7df4f7dbfd-cqlfd /bin/ps
  PID TTY          TIME CMD
    1 ?        00:00:00 gunicorn
    9 ?        00:00:05 gunicorn
   11 ?        00:00:05 gunicorn
   12 ?        00:00:05 gunicorn
   14 ?        00:00:05 gunicorn
  526 ?        00:00:00 ps
```


