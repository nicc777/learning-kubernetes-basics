#!/bin/bash

LOG_LEVEL=DEBUG
DB_HOST="jenkins-coolapp-db"
DB_PORT="5332"
DB_USER="postgres"
DB_PASS="mysecretpassword"
DB_NAME="coolapp"
SPECIFICATION_DIR="$PWD/app-src/openapi"

cd ./app-src/

echo "Build source and running unit tests"

echo "========================================"
echo "   Preparing Environment"
echo "========================================"

pip3 install coverage --upgrade
pip3 install sqlalchemy --upgrade
pip3 install connexion[swagger-ui] --upgrade
pip3 install psycopg2-binary --upgrade

echo "========================================"
echo "   Running Coverage"
echo "========================================"

$HOME/.local/bin/coverage run --source cool_app/ -m unittest


echo "DONE"

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