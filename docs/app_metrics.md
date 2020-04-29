
- [1. Strategy](#1-strategy)
- [2. Preparing to collect metrics](#2-preparing-to-collect-metrics)
  - [2.1 Installing Redis](#21-installing-redis)
  - [2.2 Testing from a POD](#22-testing-from-a-pod)
  - [2.3 Reset any Cool-App Circuit Breakers for Redis](#23-reset-any-cool-app-circuit-breakers-for-redis)
  - [2.4 Testing from a system having `kubectl` available to the cluster](#24-testing-from-a-system-having-kubectl-available-to-the-cluster)
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

# 3. Get Metrics Directly from the App (Testing)

TODO

# 4. Where to from here?

TODO