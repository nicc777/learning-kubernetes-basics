
- [1. Cool App](#1-cool-app)
- [2. Building the App (Local Testing)](#2-building-the-app-local-testing)
  - [2.1 Preparing the base container](#21-preparing-the-base-container)
  - [2.2 Build the app](#22-build-the-app)
- [3. Run the application (Local Testing)](#3-run-the-application-local-testing)
  - [3.1 Preparing to run the application for the first time](#31-preparing-to-run-the-application-for-the-first-time)
  - [3.2 Run the application](#32-run-the-application)
- [4. The Swagger UI](#4-the-swagger-ui)
- [5. Unit Tests](#5-unit-tests)
  - [5.1. Preparation for testing](#51-preparation-for-testing)
  - [5.2. Running the tests](#52-running-the-tests)

# 1. Cool App

The cool app is a simple note taking app for users. This implementation comprises of the back-end services that handle note persistence as well as user profile management.

# 2. Building the App (Local Testing)

Ensure you are in the correct working directory:

```bash
(venv) $ cd $TUTORIAL_HOME/app-src
```

## 2.1 Preparing the base container

Run the following commands:

```bash
(venv) $ docker container rm cool-app-base
(venv) $ docker image rm cool-app-base
(venv) $ cd container/base
(venv) $ docker build --no-cache -t cool-app-base .
(venv) $ cd $OLDPWD
```

## 2.2 Build the app

Run the following commands:

```bash
(venv) $ rm -frR dist/
(venv) $ python3 setup.py sdist
(venv) $ docker container rm cool-app
(venv) $ rm -frR container/app/dist
(venv) $ mkdir container/app/dist
(venv) $ cp -vf dist/* container/app/dist/
(venv) $ cp -vf openapi/* container/app/dist/
(venv) $ cd container/app
(venv) $ docker build --no-cache -t cool-app .
```

# 3. Run the application (Local Testing)

## 3.1 Preparing to run the application for the first time

First, define a network (if it doesn't already exists):

```bash
(venv) $ docker network create coolapp-net
eb7762f783b607ddecbafe790a8392e5684bfc0cb1522063bac701113e77480b
(venv) $ docker network ls
NETWORK ID          NAME                DRIVER              SCOPE
b6b44351335a        bridge              bridge              local
eb7762f783b6        coolapp-net         bridge              local
493baa9f41bf        host                host                local
8d548a8d6a9c        none                null                local
```

Check it the DB container exists:

```bash
$ docker container ls --all | grep postgres
b6acbb212160        postgres                    "docker-entrypoint.s…"    6 days ago          Exited (137) 3 days ago                                                        coolapp-db
```

If it does **_not_** exist, run the following, or skip to the marker `DB EXISTS`:

__MARKER: DB DOES NOT EXIST__

```bash
(venv) $ docker run --name coolapp-db \
--network=coolapp-net \
-p 127.0.0.1:5432:5432 \
-m 512M --memory-swap 512M \
--cpu-quota 25000 \
-e POSTGRES_PASSWORD=mysecretpassword \
-d postgres
```

__Note__: On most modern systems the CPU quota should translate to at least 1 CPU core. If you are running on a low spec machine, upp the number to at least 100000 forcing a full CPU.

Test database connectivity:

```bash
(venv) $ docker run -it --rm --network coolapp-net postgres psql -h coolapp-db -U postgres
Password for user postgres: 
psql (12.2 (Debian 12.2-2.pgdg100+1))
Type "help" for help.

postgres=# 
```

Once you have access to PostgreSQL, you can apply the SQL scripts to prepare some test data. Run the content of the following files in sequence:

1. `sql/ddl.sql`
2. `sql/initial_users.sql`
3. `sql/initial_notes.sql`

__Tip__: Using SSH port forwarding it will be possible to connect to the database using a GUI tool like [DBeaver](https://dbeaver.io/)

__MARKER: DB EXISTS__

Run the following:

```bash
(venv) $ docker container start coolapp-db
```

## 3.2 Run the application

Run the application with the following command, adjusting the various options to your needs:

```bash
(venv) $ export DEBUG=1
(venv) $ docker container stop coolapp-rest-service
(venv) $ docker container rm coolapp-rest-service
(venv) $ docker run --name coolapp-rest-service \
--network=coolapp-net \
-p 0.0.0.0:8080:8080 \
-m 512M --memory-swap 512M \
--cpu-quota 25000 \
-e SWAGGER_UI=1 \
-e LOG_LEVEL=DEBUG \
-d cool-app:latest
```

Assuming the data was loaded correctly, you should see the following with a quick curls test from your `Workstation`:

```bash
$ curl -X GET "http://192.168.0.160:8080/v1/user-profiles/search?email_address=user1%40example.tld" -H  "accept: application/json"
{
  "AccountStatus": 1,
  "UserAlias": "user1",
  "UserEmailAddress": "user1@example.tld",
  "UserId": 1,
  "UserProfileLink": "/user-profiles/1"
}
```

To see what's happening on the server, you can tail the logs on the `Server`:

```bash
(venv) $ docker logs -f coolapp-rest-service
```

```text
   .
   .
   .
--==>  2020-05-02 02:28:41,434 - DEBUG - [None] [user_profiles.py:52:load_user_profile_by_email_address] result=(1, 'user1', 'user1@example.tld', 1)

192.168.0.100 - - [02/May/2020:02:28:41 +0000] "GET /v1/user-profiles/search?email_address=user1%40example.tld HTTP/1.1" 200 148 "-" "curl/7.64.1"
```

From the response, you will see the user profile is located at `/user-profiles/1`, which you can also query:

```bash
$ curl -X GET "http://192.168.0.160:8080/v1/user-profiles/1" -H  "accept: application/json"
{
  "AccountStatus": 1,
  "UserAlias": "user1",
  "UserEmailAddress": "user1@example.tld",
  "UserId": 1,
  "UserProfileLink": "/user-profiles/1"
}
```

And the related log entries:

```text
--==>  2020-05-02 02:31:32,753 - DEBUG - [None] [user_profiles.py:76:load_user_profile_by_uid] result=(1, 'user1', 'user1@example.tld', 1)

192.168.0.100 - - [02/May/2020:02:31:32 +0000] "GET /v1/user-profiles/1 HTTP/1.1" 200 148 "-" "curl/7.64.1"
```

# 4. The Swagger UI

If you started the app with the `SWAGGER_UI=1` you can view the Swagger UI in your browser: http://192.168.0.160:8080/v1/ui/

To disable the Swagger UI, set `SWAGGER_UI=0`, or just omit it from the command line - the default value is `0` (disabled).

# 5. Unit Tests

## 5.1. Preparation for testing

The tests relies on access to a TEST database server. Ensure the Docker DB is up and running

## 5.2. Running the tests

To run unit tests with coverage (showing examples of earlier implementation efforts):

```bash
(venv) $ coverage run --source cool_app/ -m unittest
......
----------------------------------------------------------------------
Ran 6 tests in 0.010s

OK
```

Coverage report:

```bash
coverage report -m 
Name                                    Stmts   Miss  Cover   Missing
---------------------------------------------------------------------
cool_app/__init__.py                       67      7    90%   15, 26, 105, 131, 154, 178, 215
cool_app/persistence/__init__.py           28     17    39%   27-29, 36-51
cool_app/persistence/notes.py             119    119     0%   1-206
cool_app/persistence/user_profiles.py      88     88     0%   1-155
cool_app/service_app.py                   152    152     0%   8-299
---------------------------------------------------------------------
TOTAL                                     454    383    16%
```

__NOTES__:

1. You may need to set the various environment variables for the DB connection to match your test DB environment
2. 

