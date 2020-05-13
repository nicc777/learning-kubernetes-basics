#!/bin/bash

ENV_DEFAULT="state-300001"

ENV=${1:-$ENV_DEFAULT}

echo "Working with environment $ENV"

if [ -d $ENV ] 
then
    echo "info: preparing environment" 
    rm active-configs/*.yaml
    cp -vf $ENV/*.yaml active-configs/
else
    echo "critical: selected environment does not exist"
    exit 1
fi