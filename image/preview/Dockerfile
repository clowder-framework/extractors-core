FROM python:3.7-alpine

ARG VERSION="unknown"
ARG BUILDNUMBER="unknown"
ARG GITSHA1="unknown"

# environemnt variables
ENV VERSION=${VERSION} \
    BUILDNUMBER=${BUILDNUMBER} \
    GITSHA1=${GITSHA1} \
    RABBITMQ_QUEUE="ncsa.image.preview" \
    IMAGE_BINARY="/usr/bin/convert" \
    IMAGE_TYPE="png" \
    IMAGE_THUMBNAIL_COMMAND="@BINARY@ @INPUT@ -resize 225^ @OUTPUT@" \
    IMAGE_PREVIEW_COMMAND="@BINARY@ @INPUT@ -resize 800x600 @OUTPUT@"

WORKDIR /extractor

RUN apk add --no-cache imagemagick

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY binary_extractor.py extractor_info.json ./
CMD python binary_extractor.py
