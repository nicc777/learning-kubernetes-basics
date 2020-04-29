# Cool App

This is a simple demo app that can be used in Kubernetes demos

This initial README's objective is to get started. More detailed topics will be covered in the `docs/`:

* [More Basics](docs/more_basics.md)
* [All About Application Metrics](docs/app_metrics.md)

__Table of Contents for this README__

- [Cool App](#cool-app)
- [1. Local development testing](#1-local-development-testing)
  - [1.1 Prepare environment](#11-prepare-environment)
  - [1.2 Run a local server](#12-run-a-local-server)
  - [1.3 test a local server's probes](#13-test-a-local-servers-probes)
    - [1.3.1 Liveliness Probe:](#131-liveliness-probe)
    - [1.3.2 Readiness Probe:](#132-readiness-probe)
    - [1.3.3 General status:](#133-general-status)
- [2. Building the Docker Images Locally](#2-building-the-docker-images-locally)
- [3. Push the docker image to DockerHub (Public Repository)](#3-push-the-docker-image-to-dockerhub-public-repository)
- [4. Minikube Testing](#4-minikube-testing)
  - [4.1 Create a Namespace](#41-create-a-namespace)
  - [4.2 Deploy version 0.0.1](#42-deploy-version-001)
  - [4.3 Continuos Monitoring of the App](#43-continuos-monitoring-of-the-app)
  - [4.4 Force a POD restart](#44-force-a-pod-restart)
  - [4.5 Deleting the Service and Deployment](#45-deleting-the-service-and-deployment)
- [5. Monitoring Tools](#5-monitoring-tools)
  - [5.1 Prometheus](#51-prometheus)
  - [5.2 Grafana](#52-grafana)

# 1. Local development testing

## 1.1 Prepare environment

Prepare a Python virtual environment and install dependencies:

```bash
$ python3 -m venv venv
$ . venv/bin/activate
(venv) $ pip3 install flask
```

## 1.2 Run a local server

Run the following commands:

```bash
(venv) $ export FLASK_APP=cool-app/app.py 
(venv) $ flask run
```

this will expose the app on http://127.0.0.1:5000/

To expose to the network, try:

```bash
(venv) $ flask run --host=0.0.0.0
```

## 1.3 test a local server's probes

### 1.3.1 Liveliness Probe:

```bash
$ curl http://127.0.0.1:5000/probe/alive
```

OR:

```bash
while true
do curl http://127.0.0.1:5000/probe/alive
sleep .3
done
```

### 1.3.2 Readiness Probe:

```bash
$ curl http://127.0.0.1:5000/probe/ready
```

OR:

```bash
while true
do curl http://127.0.0.1:5000/probe/ready
sleep .3
done
```

### 1.3.3 General status:

```bash
$ curl http://127.0.0.1:5000/status
```

OR:

```bash
while true
do curl http://127.0.0.1:5000/status
sleep .3
done
```

# 2. Building the Docker Images Locally

Assuming the steps for local testing succeeded, the following commands will prepare first the base container:

```bash
(venv) $ docker image rm cool-app-base
(venv) $ cd container/base
(venv) $ docker build --no-cache -t cool-app-base .
(venv) $ cd $OLDPWD
```

Once the base image is built, run the build script to build the final image:

```bash
(venv) $ ./build.sh
```

Test:

```bash
(venv) $ docker run -p 0.0.0.0:8080:8080 --name cool-app cool-app
```

Once again the same tests can be run as in the previous section, including the readiness and liveliness probes.

# 3. Push the docker image to DockerHub (Public Repository)

__Important__: This is a public repository, so do not use these examples to push images that contain sensitive or proprietary information.

First, login:

```bash
(venv) $ docker login --username=yourhubusername 
Password: 
WARNING! Your password will be stored unencrypted in /home/yourhubusername/.docker/config.json.
Configure a credential helper to remove this warning. See
https://docs.docker.com/engine/reference/commandline/login/#credentials-store

Login Succeeded
```

Verify your images are available locally:

```bash
(venv) $ docker images | grep cool
cool-app                                  latest              420715366dd4        24 minutes ago      493MB
cool-app-base                             latest              b3b116e47bb3        29 minutes ago      493MB
```

And now tag and push your image:

```bash
(venv) $ docker tag 420715366dd4 yourhubusername/cool-app:0.0.1
(venv) $ docker push yourhubusername/cool-app:0.0.1
```

__Note #1__ : If you have a previous build, you will see the following from a `docker images | grep cool` command:

```text
cool-app                                  latest              c795421372ef        15 seconds ago      493MB
nicc777/cool-app                          0.0.1               67505a44d18b        23 hours ago        493MB
cool-app-base                             latest              b3b116e47bb3        37 hours ago        493MB
```

In this instance, first remove the old image (`67505a44d18b`) in this case:

```
$ docker image rm 67505a44d18b
```

Now you can tag and push the image as per normal.

__Note #2__ : If the deployment was already running and if you are developing on te same system as what minikube is running on, you may first need to delete the deployment:

```bash
$ kubectl get deployments
NAME                  READY   UP-TO-DATE   AVAILABLE   AGE
cool-app-deployment   1/1     1            1           3m20s
$ kubectl delete deployment cool-app-deployment
deployment.apps "cool-app-deployment" deleted
```

# 4. Minikube Testing

Assuming you have a [running minikube](https://kubernetes.io/docs/setup/learning-environment/minikube/) on either your local system or a server you have access to, you can deploy this app into a namespace.

## 4.1 Create a Namespace

Run the following command to create a `demo` namespace and then switch to it:

```bash
$ kubectl create namespace demo
$ kubectl config set-context --current --namespace=demo
$ kubectl config view --minify | grep namespace:
    namespace: demo
```

## 4.2 Deploy version 0.0.1

__IMPORTANT__: the files in `kubernetes/` directory refer to images created by the original author and will probably remain available on Docker Hub, although there are no guarantees. It is highly recommended that the steps in sections 2 and 3 are followed and that the files in the `kubernetes/` directory be updated to point to the new images.

Run the following command:

```bash
$ kubectl apply -f kubernetes/cool-app-0.0.1.yml
```

To verify everything was created successfully:

```bash
$ kubectl get all --show-labels
NAME                                       READY   STATUS    RESTARTS   AGE   LABELS
pod/cool-app-deployment-7df4f7dbfd-n44wp   1/1     Running   0          13s   app=cool-app,pod-template-hash=7df4f7dbfd

NAME                       TYPE           CLUSTER-IP     EXTERNAL-IP   PORT(S)        AGE   LABELS
service/cool-app-service   LoadBalancer   10.96.225.90   <pending>     80:30019/TCP   13s   <none>

NAME                                  READY   UP-TO-DATE   AVAILABLE   AGE   LABELS
deployment.apps/cool-app-deployment   1/1     1            1           13s   app=cool-app

NAME                                             DESIRED   CURRENT   READY   AGE   LABELS
replicaset.apps/cool-app-deployment-7df4f7dbfd   1         1         1       13s   app=cool-app,pod-template-hash=7df4f7dbfd
```

For easy reference, you can create environment variables for the host IP and Port numbers:

```bash
IP=$(minikube ip)
PORT=$(kubectl get service/cool-app-service -o jsonpath="{.spec.ports[*].nodePort}")
```

You can use the command `curl $IP:$PORT/status` to get a single TEXT line with the status, or you can run `open http://$IP:$PORT/` on your local development machine to open the HTML page in a web browser. The background should be a light blue color.

## 4.3 Continuos Monitoring of the App

You can monitor the status of the app by running the following command:

```bash
$ while true; do curl http://$IP:$PORT/status; sleep .3; done
pid=8    |   hostname=cool-app-deployment-7df4f7dbfd-n44wp   |   app_version=0.0.1   |   uptime=320
pid=12   |   hostname=cool-app-deployment-7df4f7dbfd-n44wp   |   app_version=0.0.1   |   uptime=320
pid=11   |   hostname=cool-app-deployment-7df4f7dbfd-n44wp   |   app_version=0.0.1   |   uptime=320
pid=11   |   hostname=cool-app-deployment-7df4f7dbfd-n44wp   |   app_version=0.0.1   |   uptime=320
pid=8    |   hostname=cool-app-deployment-7df4f7dbfd-n44wp   |   app_version=0.0.1   |   uptime=322
^C
```

## 4.4 Force a POD restart

first, check the PODS:

```bash
$ kubectl get pods --show-labels
NAME                                   READY   STATUS    RESTARTS   AGE     LABELS
cool-app-deployment-7df4f7dbfd-n44wp   1/1     Running   0          8m19s   app=cool-app,pod-template-hash=7df4f7dbfd
```

__Note__: There has been no `RESTARTS` at the moment. 

To force a restart, make a HTTP request to `/die` as follow:

```bash
$ curl http://$IP:$PORT/die
```

If you were still running the continuous monitoring as in section 4.3 you would have seen something like the following:

```bash
$ while true; do curl http://$IP:$PORT/status; sleep .3; done
pid=10   |   hostname=cool-app-deployment-7df4f7dbfd-n44wp   |   app_version=0.0.1   |   uptime=642
pid=10   |   hostname=cool-app-deployment-7df4f7dbfd-n44wp   |   app_version=0.0.1   |   uptime=642
pid=10   |   hostname=cool-app-deployment-7df4f7dbfd-n44wp   |   app_version=0.0.1   |   uptime=642
curl: (7) Failed to connect to 192.168.0.160 port 30019: Connection refused
curl: (7) Failed to connect to 192.168.0.160 port 30019: Connection refused
curl: (7) Failed to connect to 192.168.0.160 port 30019: Connection refused
curl: (7) Failed to connect to 192.168.0.160 port 30019: Connection refused
curl: (7) Failed to connect to 192.168.0.160 port 30019: Connection refused
curl: (7) Failed to connect to 192.168.0.160 port 30019: Connection refused
pid=8    |   hostname=cool-app-deployment-7df4f7dbfd-n44wp   |   app_version=0.0.1   |   uptime=6
pid=10   |   hostname=cool-app-deployment-7df4f7dbfd-n44wp   |   app_version=0.0.1   |   uptime=6
pid=8    |   hostname=cool-app-deployment-7df4f7dbfd-n44wp   |   app_version=0.0.1   |   uptime=6
```

The failing POD was unresponsive for a while while Kubernetes restarted it. On restart, Kubernetes used the readiness probe to wait until the POD was fully up _and_ ready before allowing connections again.

Also verify the `RESTARTS`:

```bash
$ kubectl get pods --show-labels
NAME                                   READY   STATUS    RESTARTS   AGE   LABELS
cool-app-deployment-7df4f7dbfd-n44wp   1/1     Running   1          16m   app=cool-app,pod-template-hash=7df4f7dbfd
```

## 4.5 Deleting the Service and Deployment

If you need to delete the service and/or deployment, run the following commands:

```bash
$ kubectl delete service cool-app-service
service "cool-app-service" deleted
$ kubectl delete deployment cool-app-deployment
deployment.apps "cool-app-deployment" deleted
```

# 5. Monitoring Tools

## 5.1 Prometheus 

__Important__: This section will soon be replaced by learnings [from this tutorial](https://sysdig.com/blog/kubernetes-monitoring-prometheus/)

## 5.2 Grafana 

__Important__ This section will soon be replaced by learnings [from this tutorial](https://sysdig.com/blog/kubernetes-monitoring-with-prometheus-alertmanager-grafana-pushgateway-part-2/)

