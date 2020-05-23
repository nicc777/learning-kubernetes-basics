#!/bin/bash

cd ./app-src/
echo "Checking if any of the Docker configurations changed"

SOURCE_BUILD_FLAG_FILE=$SRC_BUILD_FLAG_FILE
COVERAGE_PASSED_FLAG_FILE=$COVERAGE_CHECK_FILE
BUILD_COOLAPP=0
LATEST_BASE_IMAGE_URL_FILE=$DOCKERFILE_BASE_REGISTRY_FILE
LATEST_BASE_IMAGE_URL=""


echo "========================================"
echo "   Checking BASE Build Trigger"
echo "========================================"

if test -f "$DOCKER_COOLAPP_BASE_CHANGED_FILE"; then
	echo "  BASE Image changed. Proceed with build."
	BUILD_COOLAPP=1
fi

if test -f "$LATEST_BASE_IMAGE_URL_FILE"; then
	LATEST_BASE_IMAGE_URL=`cat $LATEST_BASE_IMAGE_URL_FILE`
else
	echo "  Cannot locate $LATEST_BASE_IMAGE_URL_FILE for the latest URL. FAILING."
	exit 1
fi

ls -lahrt container/app/Dockerfile
sed -i "s|FROM cool-app-base:latest|FROM $LATEST_BASE_IMAGE_URL|g" container/app/Dockerfile

echo "----------------------------------------"
echo ""
head -2 container/app/Dockerfile
echo ""
echo "----------------------------------------"

echo "========================================"
echo "   Checking Source Build Trigger"
echo "========================================"

echo "BUILD_COOLAPP=$BUILD_COOLAPP"
if [ "$BUILD_COOLAPP" == "0" ]; then
	if test -f "$SOURCE_BUILD_FLAG_FILE"; then
		if test -f "$COVERAGE_PASSED_FLAG_FILE"; then
			BUILD_COOLAPP=1
			echo "  Source change detected and coverage is in a PASSED state. Proceeding with build."
		else
			echo "  Detected source code changed, BUT, coverage either not yet run or failed. FAILING."
			exit 1
		fi
	else
		echo "  warning: $SOURCE_BUILD_FLAG_FILE does not exist"
	fi
else
	echo "  Build already set..."
fi

echo "========================================"
echo "   Checking Final Image Actions"
echo "========================================"

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
	echo "  status=$EXIT_STATUS"
	echo "  Current working directory: $PWD"
	if [ "$EXIT_STATUS" != "0" ]
	then
		echo "  COOLAPP failed to build"
		exit 1
	fi
	echo "  COOLAPP build successful"
    echo "  Pushing to registry"
    sudo docker tag cool-app:$BUILD_NUMBER $DOCKER_REGISTRY_HOST:$DOCKER_REGISTRY_PORT/cool-app:$BUILD_NUMBER
    EXIT_STATUS=$?
    if [ "$EXIT_STATUS" != "0" ]
	then
		echo "  Failed to tag image"
		exit 1
	fi
    sudo docker push $DOCKER_REGISTRY_HOST:$DOCKER_REGISTRY_PORT/cool-app
    EXIT_STATUS=$?
    if [ "$EXIT_STATUS" != "0" ]
	then
		echo "  Failed to push to the registry"
		exit 1
	fi
    echo "  Successfully pushed to the registry with tag: cool-app:$BUILD_NUMBER"

	echo "$DOCKER_REGISTRY_HOST:$DOCKER_REGISTRY_PORT/cool-app:$BUILD_NUMBER" > $LATEST_APP_IMAGE_URL_FILE
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