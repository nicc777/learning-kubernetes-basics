
- [1. Objectives of the Scenario](#1-objectives-of-the-scenario)
- [2. Technology & Patterns](#2-technology--patterns)
- [3. Step-by-Step Demo Walk Through](#3-step-by-step-demo-walk-through)
  - [3.1. Source code updates](#31-source-code-updates)
  - [3.2 Jenkins Updates](#32-jenkins-updates)
  - [3.3 Testing for failed Unit Tests in the Pipeline](#33-testing-for-failed-unit-tests-in-the-pipeline)
- [4. Scenario Discussion](#4-scenario-discussion)
  - [4.1 Trail-Map Progress](#41-trail-map-progress)
  - [4.2 Cloud-Native Principles Progress](#42-cloud-native-principles-progress)
- [5. References](#5-references)

# 1. Objectives of the Scenario 

Objectives:

* Add unit tests to our application
* Add coverage reports
* Amend our current builds to only allow the Docker images to ce created when all tests pass and the coverage is of acceptable level

For this exercise we will allow a coverage of 60% to be sufficient. It is common practice to start with a low coverage and work upwards. These are details usually decided by each team, and I'm just using any number here really - just testing a concept.

This may require introducing a build pipeline in Jenkins, although it is not always strictly required - you can do all the logic in Bash. However, as complexity grows, it make sense to start to split units of work out to more logical components that can be grouped and orchestrated in a pipe line.

# 2. Technology & Patterns

The [Agile Alliance](https://www.agilealliance.org/glossary/tdd/#q=~(infinite~false~filters~(postType~(~'page~'post~'aa_book~'aa_event_session~'aa_experience_report~'aa_glossary~'aa_research_paper~'aa_video)~tags~(~'tdd))~searchTerm~'~sort~false~sortDirection~'asc~page~1)) have a fairly good view on the definition of Test Driven Development.

The central idea is that the unit tests are written first and the initial run of a test (or tests) should fail as the feature doesn't exist yet.

Since this project starts with no unit tests, the aim will be to introduce a number of tests that aim to get the coverage above 60% as a start. Keep in mind that for very large and/or complex project, even 60% may be a big ask. 

In my mind, the ideal for this scenario is not to add any new features/functionality until the 80% coverage mark is reached. This may not be achievable in the real world, but if teams and organizations are serious about code quality, this would be what I would aim for. By the end of the day, you want to be in a position where TDD can be a viable option taking the project forward.

But why TDD? Well, I would say that forms the foundation for something called [Acceptance Test Driven Development](https://www.agilealliance.org/glossary/atdd/#q=~(infinite~false~filters~(postType~(~'page~'post~'aa_book~'aa_event_session~'aa_experience_report~'aa_glossary~'aa_research_paper~'aa_video)~tags~(~'acceptance*20test~'atdd))~searchTerm~'~sort~false~sortDirection~'asc~page~1)) which can really help test all real-world scenarios as a team learn about them and therefore ensure the best possible quality product is continuously delivered through the automated pipelines. 

Taking into account the Cloud Native principle of [Dev/prod parity](https://12factor.net/dev-prod-parity), I decided not to mock the unit tests at this stage, but to use an actual DB for the unit testing. That implies that we will also need a running DB server in the same network as the Jenkins build server.

# 3. Step-by-Step Demo Walk Through

## 3.1. Source code updates

A new version branch will be created (version 0.0.2, branch [`appsrc-0.0.2`](https://github.com/nicc777/learning-kubernetes-basics/tree/appsrc-0.0.2/app-src)) where the unit tests will be added. You checkout that branch to go through some of the practical tests documented in the README.

## 3.2 Jenkins Updates

The updated Jenkins configuration is in branch [`jenkins-0.0.2`](https://github.com/nicc777/learning-kubernetes-basics/tree/jenkins-0.0.2).

The build process is broken up into stages from which a pipeline is then put together. You now have a choice to build individual parts, or build everything.

## 3.3 Testing for failed Unit Tests in the Pipeline

In Jenkins there will be a job defined called `coolapp-coverage`. This job will run the `coverage` tests, which include running the normal unit tests. The job will fail in two cases:

* A unit test fails
* The coverage is not above a certain level

To test the effect for a failed unit test, first checkout `appsrc-0.0.2`. Then open the file `app-src/tests/test_force_fail.py` and remove the comment where applicable (it is easy to spot in the code).

Now commit and push to your origin and re-run the `coolapp-coverage` job. It should now fail.

Open the file `app-src/tests/test_force_fail.py` again and place the comment where it was previously. Commit and push to your origin and re-run the `coolapp-coverage` job, which should now pass.

# 4. Scenario Discussion

In each scenario we will map our progress against the Cloud-Native Trail Map and against the Cloud-Native Principles.

## 4.1 Trail-Map Progress

| Category                               | Technologies & Patterns Used | Progress and other notes |
|----------------------------------------|------------------------------|--------------------------|
| Containers (Docker)                    | Docker | Current application and database have been containerized |
| CI/CD                                  | Jenkins | A proper build pipeline is now available. There are still lots that can be optimized, and some aspects will probably be worked on as we progress through this project, but for the most part the `CI` portion is now considered fully functional. The `CD` portion is still outstanding. |
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
| Code Base                     | Source code is tracked in Git. Each version will have it's own branch. Each version can be independently built and deployed. |
| Dependencies                  | As part of the containerization effort, all dependencies are defined in the base and main application Docker files. There is still potential for finding a more lightweight base image to start with. The approach takes was to use the base Docker configuration to install all required software and dependencies. This image is typically build once as it will take the most time to build. The application Docker image is essentially just an installation of the latest Python application package and the build is relatively quick and is perfectly geared to be done many times. |
| Configurations                | Configuration is now done entirely through environment variable defined in the Docker configuration files. Configuration parameters can be set when launching the application. The same principle have been applied to the `CI` pipeline. |
| Backing Services              | The database server has also been containerized. The application is simple enough to not rely too much on database versions and therefore almost any version of PostgreSQL can be used. Changing from PostgreSQL to something else is relatively easy as long as that something else is supported by [SQLAlchemy](https://www.sqlalchemy.org) and only minor code changes will then be required. If this will happen often (which it shouldn't), more configuration options and a more dynamic dependency system can be considered. |
| Build, Release, Run           | The `CI` portion of the `CI/CD` pipeline have been implemented with a Jenkins build that will produce an application Docker image on the `Server`. The image is pushed to a Docker registry. |
| Processes                     | No active effort have been made to ensure the application is truly stateless. Future testing will prove this and the application will be adjusted accordingly. At the moment the application should be able to run with multiple instances. |
| Port Binding                  | This is considered completed as the application is hosted in the container and exposed via [gunicorn](https://gunicorn.org). |
| Concurrency                   | Untested but assumed to not be a problem. Will revisit during more testing in future scenarios. |
| Disposability                 | Untested but assumed to not be a problem. Will revisit during more testing in future scenarios. |
| Dev/Prod Parity               | No progress yet         |
| Logging                       | Logs are now logged to a file as well as `STDOUT`, and can be accessed via the Docker API. No log events are published yet and more work remain. |
| Admin Processes               | No progress yet         |
| API First                     | Through the use of [connexion](https://github.com/zalando/connexion) the application have been implemented with an API first principle from the start. This is considered DONE. |
| Telemetry                     | No progress yet         |
| Authentication/ Authorization | No progress yet. The application currently completely trusts the Application Server and relies on external configuration to prevent other unauthorized services connecting to it. |

# 5. References

* [Parameterized Builds in Jenkins](https://wiki.jenkins.io/display/JENKINS/Parameterized+Build)
* [Jenkins Pipelines](https://www.jenkins.io/doc/book/pipeline/)
