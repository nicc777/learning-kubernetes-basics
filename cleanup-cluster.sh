#!/bin/bash

kubectl delete namespace coolapp-dev
kubectl delete namespace coolapp-prod

rm -vf master.yaml

echo "DONE"
