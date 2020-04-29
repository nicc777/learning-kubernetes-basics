
- [Editing number of replicas in a running cluster](#editing-number-of-replicas-in-a-running-cluster)
- [Resurrecting the dead](#resurrecting-the-dead)

# Editing number of replicas in a running cluster

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

# Resurrecting the dead

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
