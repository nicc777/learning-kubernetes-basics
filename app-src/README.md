
- [1. Cool App](#1-cool-app)
- [2. Building the App](#2-building-the-app)
  - [2.1 Preparing the base container](#21-preparing-the-base-container)
  - [2.2 Build the app](#22-build-the-app)
- [3. Run the application](#3-run-the-application)
  - [3.1 Preparing to run the application for the first time](#31-preparing-to-run-the-application-for-the-first-time)
  - [3.2 Run the application](#32-run-the-application)

# 1. Cool App

The cool app is a simple note taking app for users. This implementation comprises of the back-end services that handle note persistence as well as user profile management.

# 2. Building the App

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
(venv) $ ./build.sh
```

# 3. Run the application

## 3.1 Preparing to run the application for the first time

First, define a network:

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

Next, run a PostgreSQL server:

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

## 3.2 Run the application

Run the application with the following command, adjusting the various options to your needs:

```bash
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
$ curl -X GET "http://192.168.0.160:8080/v1/user-profile?email_address=user1%40example.tld" -H  "accept: application/json"
{
  "AccountStatus": 1,
  "UserAlias": "user1",
  "UserEmailAddress": "user1@example.tld",
  "UserId": 1
}
```

To see what's happening on the server, you can tail the logs on the `Server`:

```bash
(venv) $ docker logs -f coolapp-rest-service
   .
   .
   .
--==>  2020-05-01 13:23:37,124 - DEBUG - [None] [__init__.py:88:load_user_profile] result=(1, 'user1', 'user1@example.tld', 1)

192.168.0.100 - - [01/May/2020:13:23:37 +0000] "GET /v1/user-profile?email_address=user1%40example.tld HTTP/1.1" 200 92 "-" "curl/7.64.1"
```

