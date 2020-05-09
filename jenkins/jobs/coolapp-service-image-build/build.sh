#!/bin/bash

cd ./app-src/
echo "Checking if any of the Docker configurations changed"

DOCKERFILE_BASE_CHECKSUM_FILE="docker_base_checksum"
DOCKERFILE_COOLAPP_CHECKSUM_FILE="docker_coolapp_checksum"
DOCKERFILE_BASE_CHECKSUM_OLD=""
DOCKERFILE_BASE_CHECKSUM_CURRENT=""
DOCKERFILE_COOLAPP_CHECKSUM_OLD=""
DOCKERFILE_COOLAPP_CHECKSUM_CURRENT=""
BUILD_BASE=0
BUILD_COOLAPP=0
DOCKER_REGISTRY_HOST="192.168.0.160"
DOCKER_REGISTRY_PORT="5000"


echo "========================================"
echo "   Checking BASE Docker configuration"
echo "========================================"


DOCKERFILE_BASE_CHECKSUM_CURRENT=`sha256sum ./container/base/Dockerfile | awk '{print \$1}'`
echo "   Current BASE file checksum: $DOCKERFILE_BASE_CHECKSUM_CURRENT"
if test -f "$DOCKERFILE_BASE_CHECKSUM_FILE"; then
    echo "      $DOCKERFILE_BASE_CHECKSUM_FILE exist"
    DOCKERFILE_BASE_CHECKSUM_OLD=`cat $DOCKERFILE_BASE_CHECKSUM_FILE | head -1 | awk '{print \$1}'`
    echo "   Previous BASE file checksum: $DOCKERFILE_BASE_CHECKSUM_OLD"
    if [ "$DOCKERFILE_BASE_CHECKSUM_OLD" != "$DOCKERFILE_BASE_CHECKSUM_CURRENT" ]; then
    	BUILD_BASE=1
        BUILD_COOLAPP=1
    fi
else
	echo "newfile" > $DOCKERFILE_BASE_CHECKSUM_FILE
    echo "      $DOCKERFILE_BASE_CHECKSUM_FILE created"
    BUILD_BASE=1
    BUILD_COOLAPP=1
fi

echo "      BUILD_BASE=$BUILD_BASE"

if [ "$BUILD_BASE" == "1" ]; then
	echo "      Building BASE Docker Image"
    sudo docker container rm cool-app-base
	sudo docker image rm cool-app-base
	cd container/base
    echo "      Current working directory: $PWD"
	sudo docker build --no-cache -t cool-app-base .
    EXIT_STATUS=$?
    cd $OLDPWD
    echo "      status=$EXIT_STATUS"
    echo "      Current working directory: $PWD"
    if [ "$EXIT_STATUS" != "0" ]
	then
   		echo "      BASE failed to build"
        exit 1
	fi
    echo "      BASE build successful"
    echo $DOCKERFILE_BASE_CHECKSUM_CURRENT > $DOCKERFILE_BASE_CHECKSUM_FILE
    echo "      Checksum file updated"
fi


echo "========================================"
echo "   Checking APP build history"
echo "========================================"

rm -vf /tmp/test.tar.gz
tar czf /tmp/test.tar.gz `find ./cool_app/ -type f -iname "*.py"`
DOCKERFILE_COOLAPP_CHECKSUM_CURRENT=`sha256sum ./container/base/Dockerfile | awk '{print \$1}'`
echo "   Current BASE file checksum: $DOCKERFILE_COOLAPP_CHECKSUM_CURRENT"
if test -f "$DOCKERFILE_COOLAPP_CHECKSUM_FILE"; then
    echo "      $DOCKERFILE_COOLAPP_CHECKSUM_FILE exist"
    DOCKERFILE_COOLAPP_CHECKSUM_OLD=`cat $DOCKERFILE_COOLAPP_CHECKSUM_FILE | head -1 | awk '{print \$1}'`
    echo "   Previous APP file checksum: $DOCKERFILE_COOLAPP_CHECKSUM_OLD"
    if [ "$DOCKERFILE_COOLAPP_CHECKSUM_OLD" != "$DOCKERFILE_COOLAPP_CHECKSUM_CURRENT" ]; then
    	BUILD_COOLAPP=1
    fi
else
	echo "newfile" > $DOCKERFILE_COOLAPP_CHECKSUM_FILE
    echo "      $DOCKERFILE_COOLAPP_CHECKSUM_FILE created"
    BUILD_COOLAPP=1
fi

echo "      BUILD_BASE=$BUILD_COOLAPP"

if [ "$BUILD_COOLAPP" == "1" ]; then
	rm -frR dist/
	python3 setup.py sdist
	rm -frR container/app/dist
	mkdir container/app/dist
	cp -vf dist/* container/app/dist/
	cp -vf openapi/* container/app/dist/
	cd container/app
	sudo docker build --no-cache -t cool-app:$BUILD_NUMBER .
	EXIT_STATUS=$?
	cd $OLDPWD
	echo "      status=$EXIT_STATUS"
	echo "      Current working directory: $PWD"
	if [ "$EXIT_STATUS" != "0" ]
	then
		echo "      COOLAPP failed to build"
		exit 1
	fi
	echo "      COOLAPP build successful"
    echo "      Pushing to registry"
    sudo docker tag cool-app:$BUILD_NUMBER $DOCKER_REGISTRY_HOST:$DOCKER_REGISTRY_PORT/cool-app
    EXIT_STATUS=$?
    if [ "$EXIT_STATUS" != "0" ]
	then
		echo "      Failed to tag image"
		exit 1
	fi
    sudo docker push $DOCKER_REGISTRY_HOST:$DOCKER_REGISTRY_PORT/cool-app
    EXIT_STATUS=$?
    if [ "$EXIT_STATUS" != "0" ]
	then
		echo "      Failed to push to the registry"
		exit 1
	fi
    echo "      Successfully pushed to the registry with tag: cool-app:$BUILD_NUMBER"
    echo $DOCKERFILE_COOLAPP_CHECKSUM_CURRENT > $DOCKERFILE_COOLAPP_CHECKSUM_FILE
  	echo "      Local checksum updated"  
fi

echo
echo
echo "========================================"
echo
echo "NOTE that at The moment the build needs"
echo "to be triggered manually and the APP"
echo "will build every time. Automation is WIP"
echo
echo "There is a schedule for an hourly build"
echo "but still no trigger per say."
echo
echo "========================================"