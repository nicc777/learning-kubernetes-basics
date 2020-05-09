#!/bin/bash

cd ./app-src/
echo "Build source and running unit tests"

echo "========================================"
echo "   Building Source"
echo "========================================"

rm -frR dist/
python3 setup.py sdist

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