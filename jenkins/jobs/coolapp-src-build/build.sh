#!/bin/bash

EXPECTED_FILE=$SRC_EXPECTED_FILE
OLD_CHECKSUM_FILE=$SRC_OLD_CHECKSUM_FILE
OLD_CHECKSUM_VALUE=""
NEW_CHECKSUM_VALUE=""
BUILD_FLAG_FILE=$SRC_BUILD_FLAG_FILE

rm -vf $BUILD_FLAG_FILE

cd ./app-src/
echo "Build source - Build nr $BUILD_NUMBER"

rm -frR dist/

echo "========================================"
echo "   Checking for Previous Build"
echo "========================================"

if test -f "$OLD_CHECKSUM_FILE"; then
    echo "      $OLD_CHECKSUM_FILE exist"
    OLD_CHECKSUM_VALUE=`cat $OLD_CHECKSUM_FILE | head -1 | awk '{print \$1}'`
    echo "   Previous BASE file checksum: $OLD_CHECKSUM_VALUE"
else
	echo "newfile" > $OLD_CHECKSUM_FILE
    OLD_CHECKSUM_VALUE="newfile"
    echo "      $OLD_CHECKSUM_FILE created"
fi

echo "========================================"
echo "   Updating Checksum for Source "
echo "========================================"

rm -vf /tmp/sourced_cat
cat `find ./cool_app/ -type f -iname "*.py"` > /tmp/sourced_cat
NEW_CHECKSUM_VALUE=`sha256sum /tmp/sourced_cat | awk '{print \$1}'`

echo "========================================"
echo "   Check for Building Source"
echo "========================================"

echo
if [ "$OLD_CHECKSUM_VALUE" != "$NEW_CHECKSUM_VALUE" ]; then
    python3 setup.py sdist
    ls -lahrt $EXPECTED_FILE
    if [ -f "$EXPECTED_FILE" ]; then
        echo "Build was completed succesfully"
    else
        echo "Build FAILED"
        exit 1
    fi
    touch $BUILD_FLAG_FILE
    echo "$NEW_CHECKSUM_VALUE" > $OLD_CHECKSUM_FILE
    echo "SOURCE UPDATED: TRUE"
else
     echo "SOURCE UPDATED: FALSE"
fi
echo

echo "========================================"
echo "   DONE"
echo "========================================"

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