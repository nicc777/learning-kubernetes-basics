---
name: Cool-App Bug report
about: Log a bug for the Cool-App
title: ''
labels: bug
assignees: nicc777

---

# Describe the bug

A clear and concise description of what the bug is.

# To Reproduce

Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

# Expected behaviour

A clear and concise description of what you expected to happen.

# Diagnostics

Paste the output of the following commands as run on your Kubernetes/Minikube cluster:

```bash
$ kubectl get namespaces
$ kubectl get all --show-labels
$ kubectl config view --minify | grep namespace:
$ docker -v
$ cat /etc/os-release 
```

Paste the output of the following commands as run on your development system containing this repo:

```bash
$ python3 -V
$ git status | grep "On branch"
$ docker -v
$ cat /etc/os-release 
```

Finally, paste the relevant LOG entries you obtained from a running POD or the running app

# Scenario Branch

Note the branch you noticed this issue in

# Additional context

Add any other context about the problem here.
