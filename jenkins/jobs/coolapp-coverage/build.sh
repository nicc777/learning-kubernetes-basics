#!/bin/bash

export LOG_LEVEL=DEBUG
export SPECIFICATION_DIR="$PWD/app-src/openapi"
export DB_HOST=$COVERAGE_TEST_DB_HOST
export DB_POST=$COVERAGE_TEST_DB_PORT
export DB_USER=$COVERAGE_TEST_DB_USER
export DB_PASS=$COVERAGE_TEST_DB_PASS
export DB_NAME=$COVERAGE_TEST_DB_NAME
#COVERAGE_MINIMUM="60"

cd ./app-src/

echo "Build source and running unit tests"
echo "COVERAGE_MINIMUM=$COVERAGE_MINIMUM"

echo "========================================"
echo "   Preparing Environment"
echo "========================================"

rm -vf $COVERAGE_CHECK_FILE
pip3 install coverage --upgrade
pip3 install sqlalchemy --upgrade
pip3 install connexion[swagger-ui] --upgrade
pip3 install psycopg2-binary --upgrade
pip3 install circuitbreaker --upgrade

echo "========================================"
echo "   Running Coverage"
echo "========================================"

echo "SPECIFICATION_DIR=$SPECIFICATION_DIR"

$HOME/.local/bin/coverage run --source cool_app/ -m unittest
EXIT_STATUS=$?
if [ "$EXIT_STATUS" != "0" ]
then
    echo "      Testing FAILED"
    exit 1
fi
$HOME/.local/bin/coverage report -m > /tmp/coverage_detail.txt
cat /tmp/coverage_detail.txt
COVERAGE_PERCENTAGE=`cat /tmp/coverage_detail.txt | tail -1 | awk '{print \$4}' | awk -F\\% '{print \$1}'`
echo "** COVERAGE_PERCENTAGE = $COVERAGE_PERCENTAGE"
echo "** COVERAGE_MINIMUM    = $COVERAGE_MINIMUM"
if [ "$COVERAGE_PERCENTAGE" -lt "$COVERAGE_MINIMUM" ]
then
    echo "      Coverage minimum check FAILED"
    exit 1
fi
echo "      Minimum coverage level was satisfied."
touch $COVERAGE_CHECK_FILE

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