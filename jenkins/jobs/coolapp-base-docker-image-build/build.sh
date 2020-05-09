#!/bin/bash

cd ./app-src/
echo "Checking if any of the Docker configurations changed"

DOCKERFILE_BASE_CHECKSUM_FILE="docker_base_checksum"
DOCKERFILE_BASE_BUILD_ACTION_FILE="docker_base_build_action"
DOCKERFILE_BASE_REGISTRY_FILE="docker_base_registry"
DOCKERFILE_BASE_CHECKSUM_OLD=""
DOCKERFILE_BASE_CHECKSUM_CURRENT=""
BUILD_BASE=0
DOCKER_REGISTRY_HOST="192.168.0.160"
DOCKER_REGISTRY_PORT="5000"


echo "========================================"
echo "   Checking BASE Docker configuration"
echo "========================================"


echo "0" > $DOCKERFILE_BASE_BUILD_ACTION_FILE
DOCKERFILE_BASE_CHECKSUM_CURRENT=`sha256sum ./container/base/Dockerfile | awk '{print \$1}'`
echo "   Current BASE file checksum: $DOCKERFILE_BASE_CHECKSUM_CURRENT"
if test -f "$DOCKERFILE_BASE_CHECKSUM_FILE"; then
    echo "      $DOCKERFILE_BASE_CHECKSUM_FILE exist"
    DOCKERFILE_BASE_CHECKSUM_OLD=`cat $DOCKERFILE_BASE_CHECKSUM_FILE | head -1 | awk '{print \$1}'`
    echo "   Previous BASE file checksum: $DOCKERFILE_BASE_CHECKSUM_OLD"
    if [ "$DOCKERFILE_BASE_CHECKSUM_OLD" != "$DOCKERFILE_BASE_CHECKSUM_CURRENT" ]; then
    	BUILD_BASE=1
    fi
else
	echo "newfile" > $DOCKERFILE_BASE_CHECKSUM_FILE
    echo "      $DOCKERFILE_BASE_CHECKSUM_FILE created"
    BUILD_BASE=1
fi

echo "      BUILD_BASE=$BUILD_BASE"

if [ "$BUILD_BASE" == "1" ]; then
	echo "      Building BASE Docker Image"
    sudo docker container rm cool-app-base
	sudo docker image rm cool-app-base
	cd container/base
    echo "      Current working directory: $PWD"
	sudo docker build --no-cache -t cool-app-base:$BUILD_NUMBER .
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
    
    echo "      Pushing to registry"
    sudo docker tag cool-app-base:$BUILD_NUMBER $DOCKER_REGISTRY_HOST:$DOCKER_REGISTRY_PORT/cool-app-base
    EXIT_STATUS=$?
    if [ "$EXIT_STATUS" != "0" ]
	then
		echo "      Failed to tag image"
		exit 1
	fi
    sudo docker push $DOCKER_REGISTRY_HOST:$DOCKER_REGISTRY_PORT/cool-app-base
    EXIT_STATUS=$?
    if [ "$EXIT_STATUS" != "0" ]
	then
		echo "      Failed to push to the registry"
		exit 1
	fi
    echo "      Successfully pushed to the registry with tag: cool-app-base:$BUILD_NUMBER"
    echo "cool-app-base:$BUILD_NUMBER" > $DOCKERFILE_BASE_REGISTRY_FILE
    
    
    echo $DOCKERFILE_BASE_CHECKSUM_CURRENT > $DOCKERFILE_BASE_CHECKSUM_FILE
    echo "      Checksum file updated"
    echo "1" > $DOCKERFILE_BASE_BUILD_ACTION_FILE
fi


