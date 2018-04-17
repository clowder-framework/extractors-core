#!/bin/bash

# exit on error, with error code
set -e

# can use the following to push to isda-registry for testing:
# BRANCH="master" SERVER=isda-registry.ncsa.illinois.edu/ ./release.sh

# use DEBUG=echo ./release.sh to print all commands
export DEBUG=${DEBUG:-""}

# use SERVER=XYZ/ to push to a different server
SERVER=${SERVER:-""}

# what branch are we on
BRANCH=${BRANCH:-"$(git rev-parse --abbrev-ref HEAD)"}

# make sure docker is build
$(dirname $0)/docker.sh

# find out the version
if [ "${BRANCH}" == "master" ]; then
    VERSION=${VERSION:-"2.0.0 2.0 2 latest"}
elif [ "${BRANCH}" == "develop" ]; then
    VERSION="develop"
else
    exit 0
fi

# tag all images and push if needed
for x in $( find . -name Dockerfile ); do
    FOLDER=$( echo $x | sed 's#./\(.*\)/Dockerfile#\1#' )
    if [ ! "$FOLDER" = "audio/speech2text" ]; then
        NAME=$( echo "$FOLDER" | sed 's#/#-#g' )
        for v in ${VERSION}; do
            if [ "$v" != "latest" -o "$SERVER" != "" ]; then
                ${DEBUG} docker tag clowder/extractors-${NAME}:latest ${SERVER}clowder/extractors-${NAME}:${v}
            fi
            ${DEBUG} docker push ${SERVER}clowder/extractors-${NAME}:${v}
        done
    fi
done
