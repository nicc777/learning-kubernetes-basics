#!/bin/sh

# first build the python app
rm -frR dist/
python3 setup.py sdist

# build te docker image
docker container rm cool-app
rm -frR container/app/dist
mkdir container/app/dist
cp -vf dist/* container/app/dist/
cd container/app
docker build --no-cache -t cool-app .

