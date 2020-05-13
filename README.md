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
