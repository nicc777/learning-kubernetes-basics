#!/bin/bash

MASTER_FILE="master.yaml"
ENV_DEFAULT="state-300001"
ENV=${1:-$ENV_DEFAULT}

echo "info: Working with environment $ENV"

if [ -d $ENV ] 
then
    echo "info: preparing environment" 
    rm active-configs/*.yaml
    cp -vf $ENV/*.yaml active-configs/
    kubectl kustomize active-configs/ > $MASTER_FILE
    EXIT_STATUS=$?
    if [ "$EXIT_STATUS" != "0" ]
	then
		echo "error: kustomize command failed"
		exit 1
	fi
    if [ -f "$MASTER_FILE" ]; then
        echo "info: file $MASTER_FILE created."
    else 
        echo "error: failed to create the $MASTER_FILE"
    fi
else
    echo "error: selected environment does not exist"
    exit 1
fi

echo "DONE"
