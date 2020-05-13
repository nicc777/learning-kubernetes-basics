
- [Pre-requisites](#pre-requisites)
- [Preparing a Configuration Set](#preparing-a-configuration-set)
- [Applying the master config](#applying-the-master-config)
- [When deleting a namespace gets stuck](#when-deleting-a-namespace-gets-stuck)

# Pre-requisites

Ensure you run the commands on a system with `kubectl` installed and correctly configured for the correct environment.

In the development environment it's a could idea to start each `Scenario` with a clean slate, so you can also run the clean-up script:

```bash
$ ./cleanup-cluster.sh 
namespace "coolapp-dev" deleted
namespace "coolapp-prod" deleted
DONE
```

__Note__: This action may take some time.

# Preparing a Configuration Set

Make sure you know which state set you would like to use. Each set will be in a directory called `./state-nnnnnn`.

The `nnnnnn` portion should correspond with a `Scenario` branch.

To prepare the master configuration, run the following command:

```bash
./set-env.sh state-nnnnnn
info: Working with environment state-300001
info: preparing environment
'state-300001/kustomization.yaml' -> 'active-configs/kustomization.yaml'
'state-300001/namespaces.yaml' -> 'active-configs/namespaces.yaml'
   .
   .
   .
info: file master.yaml created.
DONE
```

# Applying the master config

Run the following to apply the master config:

```bash
$ kubectl apply -f master.yaml 
namespace/coolapp-dev created
namespace/coolapp-prod created
   .
   .
   .
```

# When deleting a namespace gets stuck

When the command appears to be unable to finish, you may find that a namespace appears to be "stuck" in a `Terminating` state:

```bash
$ kubectl get namespaces
NAME                   STATUS        AGE
coolapp-prod           Terminating   22m
```

Do the following to fix this, using `coolapp-prod` as an example:

```bash
kubectl get namespace coolapp-prod -o json > coolapp-prod.json
```

The resulting JSON file will look something like this:

```json
{
    "apiVersion": "v1",
    "kind": "Namespace",
    "metadata": {
        "annotations": {
            "kubectl.kubernetes.io/last-applied-configuration": "{\"apiVersion\":\"v1\",\"kind\":\"Namespace\",\"metadata\":{\"annotations\":{},\"name\":\"coolapp-prod\"}}\n"
        },
        "creationTimestamp": "2020-05-13T03:52:53Z",
        "deletionTimestamp": "2020-05-13T04:15:04Z",
        "name": "coolapp-prod",
        "resourceVersion": "2892639",
        "selfLink": "/api/v1/namespaces/coolapp-prod",
        "uid": "7ada77db-bc27-450d-94dd-e630e0e07d1c"
    },
    "spec": {
        "finalizers": [
            "kubernetes"
        ]
    },
    "status": {
        "phase": "Terminating"
    }
}
```

You need to delete the line with `"kubernetes"` in (line 17 in the example above).

Save the file and run the following:

```bash
$ kubectl replace --raw "/api/v1/namespaces/coolapp-prod/finalize" -f ./coolapp-prod.json
{"kind":"Namespace","apiVersion":"v1","metadata":{"name":"coolapp-prod","selfLink":"/api/v1/namespaces/coolapp-prod/finalize","uid":"7ada77db-bc27-450d-94dd-e630e0e07d1c","resourceVersion":"2892639","creationTimestamp":"2020-05-13T03:52:53Z","deletionTimestamp":"2020-05-13T04:15:04Z","annotations":{"kubectl.kubernetes.io/last-applied-configuration":"{\"apiVersion\":\"v1\",\"kind\":\"Namespace\",\"metadata\":{\"annotations\":{},\"name\":\"coolapp-prod\"}}\n"}},"spec":{},"status":{"phase":"Terminating"}}
```

The namespace should now be gone.
