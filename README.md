
- [1. Objectives of the Scenario](#1-objectives-of-the-scenario)
- [2. Technology & Patterns](#2-technology--patterns)
- [3. Step-by-Step Demo Walk Through](#3-step-by-step-demo-walk-through)
- [4. Scenario Discussion](#4-scenario-discussion)
  - [4.1 Trail-Map Progress](#41-trail-map-progress)
  - [4.2 Cloud-Native Principles Progress](#42-cloud-native-principles-progress)
- [5. References](#5-references)

# 1. Objectives of the Scenario

The objective of this scenario is more focused around the source code and more specifically refactoring around the `Circuit Breaker` patterns in order to cater for several scenarios within the `microservices` context that may see our application handling requests with some issue on the database (either it's still starting up, or there is some maintenance happening, making it unavailable).

# 2. Technology & Patterns

The primary pattern that will be implemented in this scenario is the [The Circuit Breaker Pattern](https://martinfowler.com/bliki/CircuitBreaker.html).

By extensive use of unit tests, various scenarios will be simulated where the database is unavailable.

# 3. Step-by-Step Demo Walk Through

TODO

# 4. Scenario Discussion

Referring to version 0.0.2 of the source code, you may notice that the database calls required for each object is embedded in the classes for `User Profiles` and `Notes`. An example can be seen in the [`notes` module](https://github.com/nicc777/learning-kubernetes-basics/blob/appsrc-0.0.2/app-src/cool_app/persistence/notes.py).

We already have a number of unit tests to test the positive cases of the various operations. The unit tests will be adapted to cater for testing cases where the database is unavailable. The tests will also test scenarios where connectivity is unavailable for a certain time. These tests will form the bases for testing our `Circuit Breaker`.

The refactoring exercise will move the database calls out of the `User Profiles` and `Notes` classes and into dedicated database related functions. We will thereby rid the user profile and note objects from any back-end logic.

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

* [The Circuit Breaker Pattern](https://martinfowler.com/bliki/CircuitBreaker.html) by Martin Fowler
* [Python Circuit Breaker Pattern Implementation](https://pypi.org/project/circuitbreaker/)
  * You can also consider to [fork the repo](https://github.com/fabfuel/circuitbreaker) to experiment on your own.

