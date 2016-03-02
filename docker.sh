#!/bin/sh

# variables that can be set
# DEBUG   : set to echo to print command and not execute
# PUSH    : set to push to push, anthing else not to push. If not set
#           the program will push if master or develop.
# PROJECT : the project to add to the image, default is NCSA

#DEBUG=echo

# make sure PROJECT ends with /
PROJECT=${PROJECT:-"ncsa"}
if [ ! "${PROJECT}" = "" -a ! "$( echo $PROJECT | tail -c 2)" = "/" ]; then
  PROJECT="${PROJECT}/"
fi

# make sure PROJECT ends with /
if [ ! "${PROJECT}" = "" ]; then
  if [ ! "$( echo $PROJECT | tail -c 2)" = "/" ]; then
    PROJECT="${PROJECT}/"
  fi
fi

# find out version and if we should push
BRANCH="$(git rev-parse --abbrev-ref HEAD)"
VERSION=${VERSION:-""}
if [ "$VERSION" = "" ]; then
  VERSION="$(git tag --points-at HEAD)"
  if [ "$BRANCH" = "master" ]; then
    PUSH=${PUSH:-"push"}
    VERSION="${VERSION} latest"
  elif [ "$BRANCH" = "develop" ]; then
    PUSH=${PUSH:-"push"}
    VERSION="${VERSION} latest"
  else
    PUSH=${PUSH:-""}
  fi
else
  PUSH=${PUSH:-""}
fi

# keep track of which latest amde
LATEST=""

# helper to create the docker container
# $1 - folder that contains the Dockerfile
# $2 - name of docker image
create() {
  if [ -z "$1" ]; then echo "Missing repo/Dockerfile name."; exit -1; fi
  if [ ! -e "$1/Dockerfile" ]; then echo "Missing Dockerfile in $1."; exit -1; fi
  if [ -z "$2" ]; then echo "Missing name for $1."; exit -1; fi

  # create image using temp id
  local ID=$(uuidgen)
  ${DEBUG} docker build --pull --tag $$ $1
  if [ $? -ne 0 ]; then
    echo "FAILED build of $1/Dockerfile"
    exit -1
  fi

  # tag all versions
  for v in $VERSION; do
    ${DEBUG} docker tag $$ ${PROJECT}${2}:${v}
    if [ "$PUSH" = "push" -a ! "$PROJECT" = "" ]; then
      ${DEBUG} docker push ${PROJECT}${2}:${v}
    fi
  done

  # tag version as latest, but don't push
  if [ ! "$BRANCH" = "master" ]; then
    ${DEBUG} docker tag $$ ${PROJECT}${2}:latest
    LATEST="$LATEST $2"
  fi

  # delete image with temp id
  ${DEBUG} docker rmi $$
}

# Create the docker containers
for FOLDER in */*; do
  if [ ! "$FOLDER" = "audio/speech2text" ]; then
    NAME=$( echo "$FOLDER" | sed 's#/#-#g' )
    create "${FOLDER}" "clowder-extractors-${NAME}"
  fi
done

# remove latest tags
for r in $LATEST; do
  ${DEBUG} docker rmi ${PROJECT}${r}:latest
done
