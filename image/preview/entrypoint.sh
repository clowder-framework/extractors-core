#!/bin/bash

if [ "$1" == "extractor" ]; then
  sed -e "s#name=\"memory\" value=\".*#name=\"memory\" value=\"${IMAGE_RESOURCE_MEMORY}\"/>#" \
      -e "s#name=\"disk\" value=\".*#name=\"disk\" value=\"${IMAGE_RESOURCE_DISK}\"/>#" \
      -e "s#name=\"width\" value=\".*#name=\"width\" value=\"${IMAGE_RESOURCE_PIXELS}\"/>#" \
      -e "s#name=\"height\" value=\".*#name=\"height\" value=\"${IMAGE_RESOURCE_PIXELS}\"/>#" \
      -i /etc/ImageMagick-6/policy.xml
  echo "----------------------------------------------------------------------"
  convert -list resource
  echo "----------------------------------------------------------------------"
  exec python binary_extractor.py
else
  exec $@
fi
