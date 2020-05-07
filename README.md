
- [1. Objectives of the Scenario](#1-objectives-of-the-scenario)
- [2. Technology & Patterns](#2-technology--patterns)
- [3. Step-by-Step Demo Walk Through](#3-step-by-step-demo-walk-through)
  - [3.1. Source code updates](#31-source-code-updates)
  - [3.2 Jenkins Updates](#32-jenkins-updates)
  - [3.3 Testing for failed Unit Tests in the Pipeline](#33-testing-for-failed-unit-tests-in-the-pipeline)
  - [3.3 Testing for Code Coverage in the Pipeline](#33-testing-for-code-coverage-in-the-pipeline)
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

# 3. Step-by-Step Demo Walk Through

## 3.1. Source code updates

A new version branch will be created (version 0.0.2, branch `appsrc-0.0.2`) where the unit tests will be added. You checkout that branch to go through some of the practical tests documented in the README.

## 3.2 Jenkins Updates

TODO

## 3.3 Testing for failed Unit Tests in the Pipeline

TODO

## 3.3 Testing for Code Coverage in the Pipeline

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