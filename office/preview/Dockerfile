FROM python:3.7-alpine

ARG VERSION="unknown"
ARG BUILDNUMBER="unknown"
ARG GITSHA1="unknown"

# environemnt variables
ENV VERSION=${VERSION} \
    BUILDNUMBER=${BUILDNUMBER} \
    GITSHA1=${GITSHA1} \
    RABBITMQ_QUEUE="ncsa.office.preview" \
    IMAGE_BINARY="/usr/bin/convert" \
    IMAGE_TYPE="png" \
    IMAGE_THUMBNAIL_COMMAND="@BINARY@ @INPUT@[0] -density 300 -resize 225^ @OUTPUT@" \
    IMAGE_PREVIEW_COMMAND="" \
    PREVIEW_BINARY="/usr/bin/libreoffice" \
    PREVIEW_TYPE="pdf" \
    PREVIEW_COMMAND="@BINARY@ --headless --convert-to pdf @INPUT@"

WORKDIR /extractor

RUN apk add --no-cache imagemagick libreoffice

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY ncsa.office.preview.py extractor_info.json ./
CMD python ncsa.office.preview.py
