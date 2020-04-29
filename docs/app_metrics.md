
- [1. Strategy](#1-strategy)
- [2. Preparing to collect metrics](#2-preparing-to-collect-metrics)
  - [2.1 Installing Redis](#21-installing-redis)
  - [2.2 Testing from a POD](#22-testing-from-a-pod)
  - [2.3 Reset any Cool-App Circuit Breakers for Redis](#23-reset-any-cool-app-circuit-breakers-for-redis)
  - [2.4 Testing from a system having `kubectl` available to the cluster](#24-testing-from-a-system-having-kubectl-available-to-the-cluster)
  - [2.5 Testing from the running POD using the actual application](#25-testing-from-the-running-pod-using-the-actual-application)
- [3. Get Metrics Directly from the App (Testing)](#3-get-metrics-directly-from-the-app-testing)
- [4. Where to from here?](#4-where-to-from-here)

# 1. Strategy

TODO

# 2. Preparing to collect metrics

TODO

## 2.1 Installing Redis

Using [helm](https://helm.sh/), install [Redis](https://redis.io/) using the following command:

```bash
$ helm install cool-app-redis --set usePassword=false  bitnami/redis
NAME: cool-app-redis
LAST DEPLOYED: Wed Apr 29 13:24:02 2020
NAMESPACE: demo
STATUS: deployed
REVISION: 1
TEST SUITE: None
NOTES:
** Please be patient while the chart is being deployed **
Redis can be accessed via port 6379 on the following DNS names from within your cluster:

cool-app-redis-master.demo.svc.cluster.local for read/write operations
cool-app-redis-slave.demo.svc.cluster.local for read-only operations

To connect to your Redis server:

1. Run a Redis pod that you can use as a client:

   kubectl run --namespace demo cool-app-redis-client --rm --tty -i --restart='Never' \
   --image docker.io/bitnami/redis:5.0.9-debian-10-r0 -- bash

2. Connect using the Redis CLI:
   redis-cli -h cool-app-redis-master
   redis-cli -h cool-app-redis-slave

To connect to your database from outside the cluster execute the following commands:

    kubectl port-forward --namespace demo svc/cool-app-redis-master 6379:6379 &
    redis-cli -h 127.0.0.1 -p 6379
```

__Important Security Notice__: The Redis instance runs without authentication. This will probably change in the future or may even be examined in a different branch. Keep an eye open for this changes.

## 2.2 Testing from a POD

TODO

## 2.3 Reset any Cool-App Circuit Breakers for Redis

TODO

## 2.4 Testing from a system having `kubectl` available to the cluster

The following is an example session getting the metrics while the Cool-App was running:

```bash
$ kubectl run --namespace demo cool-app-redis-client --rm --tty -i --restart='Never' --image docker.io/bitnami/redis:5.0.9-debian-10-r0 -- bash
If you dont see a command prompt, try pressing enter.
I have no name!@cool-app-redis-client:/$ redis-cli -h cool-app-redis-master
cool-app-redis-master:6379> KEYS *-resource
1) "metrics-get-counter-resource"
2) "probe-alive-resource"
3) "status-resource"
4) "metrics-get-circuit-breakers-resource"
5) "probe-ready-resource"
cool-app-redis-master:6379> GET "probe-alive-resource"
"133"
cool-app-redis-master:6379> GET "status-resource"
"1212"
cool-app-redis-master:6379> 
I have no name!@cool-app-redis-client:/$ exit
pod "cool-app-redis-client" deleted
```

## 2.5 Testing from the running POD using the actual application

In this example, a `bash` session will be opened on a running POD and then the deployed app will be used to test a number of functions by hand

A typical session:

```bash
$ kubectl exec -it cool-app-deployment-7df4f7dbfd-44fbn /bin/bash
root@cool-app-deployment-7df4f7dbfd-44fbn:/usr/src/app# cd /usr/local/lib/python3.6/dist-packages/cool-app/
root@cool-app-deployment-7df4f7dbfd-44fbn:/usr/local/lib/python3.6/dist-packages/cool-app# python3
Python 3.6.9 (default, Apr 18 2020, 01:56:04) 
[GCC 8.4.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import app
>>> app.get_redis_error_count()
[pid=57] warning: failed to initialize redis_error file. If this message repeats often, kill the POD
Traceback (most recent call last):
  File "/usr/local/lib/python3.6/dist-packages/cool-app/app.py", line 66, in get_redis_error_count
    result = os.path.getsize('redis_error')
  File "/usr/lib/python3.6/genericpath.py", line 50, in getsize
    return os.stat(filename).st_size
FileNotFoundError: [Errno 2] No such file or directory: 'redis_error'
[pid=57] warning: can not determine redis file size - returning 0
0
>>> app.record_hit(key='test', value=5)
[pid=57] info: get_redis_error_count(): result=0
[pid=57] info: record_hit(): Hits will be recorded again from the next attempt
>>> app.record_hit(key='test', value=5)
>>> app.get_metric_by_key(name='test')
5
>>> app.record_hit(key='test', value=7)
>>> app.get_metric_by_key(name='test')
12
>>> app.metrics_get_circuit_breakers()
[pid=57] info: get_redis_error_count(): result=0
{'Redis': {'Flag': 0, 'Counter': 0}}
>>> app.metrics_get_stats(name='test')
'12'
```

# 3. Get Metrics Directly from the App (Testing)

TODO

# 4. Where to from here?

TODO