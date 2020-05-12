
- [1. Objectives of the Scenario](#1-objectives-of-the-scenario)
- [2. Technology & Patterns](#2-technology--patterns)
  - [2.1. The Setup](#21-the-setup)
  - [2.2. Laying the Foundations for GitOps](#22-laying-the-foundations-for-gitops)
- [3. Step-by-Step Demo Walk Through](#3-step-by-step-demo-walk-through)
- [4. Scenario Discussion](#4-scenario-discussion)
  - [4.1 Trail-Map Progress](#41-trail-map-progress)
  - [4.2 Cloud-Native Principles Progress](#42-cloud-native-principles-progress)
- [5. References](#5-references)

# 1. Objectives of the Scenario 

In this scenario, I want to start the application and database in a Kubernetes cluster, where the application is exposed as a Kubernetes service.

There are also a number of foundational tasks, for example the establishment of GitOps principles.

# 2. Technology & Patterns

Apart from focusing on [Kubernetes](https://kubernetes.io/), the actual implementation in the lab environment will be done using [Minikube](https://kubernetes.io/docs/setup/learning-environment/minikube/), which is a learning environment for Kubernetes. Towards the end of this series of scenarios I will look at how to deploy to an actual production Kubernetes cluster, but for now, I will stick with Minikube for the remainder of the scenarios.

Having stated that principle, it is also a good opportunity to experiment with how to run different environments within the cluster. For example, we may want a development-testing environment (where developers can test), a more stable formal testing environment and then a production environment. All these different environments can be achieved in Kubernetes by using [namespaces](https://kubernetes.io/docs/concepts/overview/working-with-objects/namespaces/).

## 2.1. The Setup

([click on the image for a larger version](images/kubernetes_environment.png))

<center><a href="images/kubernetes_environment.png"><img src="images/kubernetes_environment.png" alt="Trail Map" width="350" height="236"></a></center>

## 2.2. Laying the Foundations for GitOps

GitOps have been described by several sources, but I found the following two to stand out:

* [Atlassian GitOps Reference](https://www.atlassian.com/git/tutorials/gitops)
* These two articles from WeaveWorks:
  * [What is GitOps](https://www.weave.works/blog/what-is-gitops-really); and
  * [GitOps - Operations by Pull Request](https://www.weave.works/blog/gitops-operations-by-pull-request)

I need to spend some time on the topic as I believe it is especially important and relevant for establishing proper governance in Agile development environments within regulated organizations. After all, all actions must be traceable and linked to individual users with the right authority giving permission - also known as a change management process.

There have been many debates over the years of how to establish proper change management governance within agile teams and I believe GitOps truly satisfy all the requirements:

* There is a defined process
* Users must be authenticated before they can perform actions
* All actions are logged
* Within each step of the process, minimum requirements can be defined and enforced
* The next step will not kick off if the previous step have not been properly signed off as per all the requirements

It is important to note at this point that different Git technologies will give you different features and options in putting together a process that will meet the governance requirements of your particular organization. You also have to take into account your entire eco system, including your project management tools etc.

Here is a short list of some popular options you may need to consider:

* The [Atlassian](https://www.atlassian.com) stack
* [Azure DevOps](https://azure.microsoft.com/en-us/services/devops/), formerly known as [TFS](https://docs.microsoft.com/en-us/azure/devops/server/tfs-is-now-azure-devops-server?view=azure-devops)
  * __Note__: [Microsoft acquired GitHub](https://news.microsoft.com/2018/06/04/microsoft-to-acquire-github-for-7-5-billion/) in 2018, and I think it would be reasonable to assume that the GitHub support withing Azure DevOps will improve over time. Here is some [documentation](https://docs.microsoft.com/en-us/azure/devops/boards/github/?toc=%2Fazure%2Fdevops%2Fboards%2Ftoc.json&bc=%2Fazure%2Fdevops%2Fboards%2Fbreadcrumb%2Ftoc.json&view=azure-devops) on how to integrate Azure DevOps and GitHub.

In all the scenarios, however, I am not focusing on the practice of the various techniques as this will differ from team to team, and I will just be using normal GitHub throughout. 

# 3. Step-by-Step Demo Walk Through

TODO

# 4. Scenario Discussion

TODO

In each scenario we will map our progress against the Cloud-Native Trail Map and against the Cloud-Native Principles.

## 4.1 Trail-Map Progress

| Category                               | Technologies & Patterns Used | Progress and other notes |
|----------------------------------------|------------------------------|--------------------------|
| Containers (Docker)                    | n/a                          | not started yet          |
| CI/CD                                  | n/a                          | not started yet          |
| Orchestration & Application Definition | n/a                          | not started yet          |
| Observability and Analysis             | n/a                          | not started yet          |
| Service Proxy, Discovery & Mesh        | n/a                          | not started yet          |
| Networking, Policy & Security          | n/a                          | not started yet          |
| Distributed Database & Storage         | n/a                          | not started yet          |
| Streaming & Messaging                  | n/a                          | not started yet          |
| Container Registry & Runtime           | n/a                          | not started yet          |
| Software Distribution                  | n/a                          | not started yet          |

## 4.2 Cloud-Native Principles Progress

| Factor                        | Progress and Discussion |
|-------------------------------|-------------------------|
| Code Base                     | No progress yet         |
| Dependencies                  | No progress yet         |
| Configurations                | No progress yet         |
| Backing Services              | No progress yet         |
| Build, Release, Run           | No progress yet         |
| Processes                     | No progress yet         |
| Port Binding                  | No progress yet         |
| Concurrency                   | No progress yet         |
| Disposability                 | No progress yet         |
| Dev/Prod Parity               | No progress yet         |
| Logging                       | No progress yet         |
| Admin Processes               | No progress yet         |
| API First                     | No progress yet         |
| Telemetry                     | No progress yet         |
| Authentication/ Authorization | No progress yet         |

# 5. References

TODO