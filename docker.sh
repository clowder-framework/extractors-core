#!/bin/sh

# exit on error, with error code
set -e

# use DEBUG=echo ./release.sh to print all commands
DEBUG=${DEBUG:-""}

# Create the docker containers
for x in $( find . -name Dockerfile ); do
  FOLDER=$( echo $x | sed 's#./\(.*\)/Dockerfile#\1#' )
  if [ ! "$FOLDER" = "audio/speech2text" ]; then
    NAME=$( echo "$FOLDER" | sed 's#/#-#g' )
    ${DEBUG} docker build -t clowder/extractors-${NAME}:latest ${FOLDER}
  fi
done
