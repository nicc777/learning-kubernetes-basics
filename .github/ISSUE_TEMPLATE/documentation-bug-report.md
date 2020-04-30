---
name: Documentation Bug report
about: Notice a typo? Steps in the documentation not working?
title: ''
labels: bug, documentation
assignees: nicc777

---

# Describe the bug

A clear and concise description of what the bug is.

# Documentation File

The name of the Markdown file containing the error

# Scenario Branch

The branch you noticed this issue in

# Section(s) and/or Paragraph(s)/Line(s) with the issue

List the section(s) where the issue is and give some context on where exactly the issue lies.

# Screenshots or Terminal Session Capture

If you followed steps that didn't work, provide a screenshot or session capture here to show what the error was.

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

# Additional context

Add any other context about the problem here.
