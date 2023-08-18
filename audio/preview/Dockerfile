FROM python:3.7-alpine

ARG VERSION="unknown"
ARG BUILDNUMBER="unknown"
ARG GITSHA1="unknown"

# environemnt variables
ENV VERSION=${VERSION} \
    BUILDNUMBER=${BUILDNUMBER} \
    GITSHA1=${GITSHA1} \
    CLOWDER_VERSION=1 \
    RABBITMQ_QUEUE="ncsa.audio.preview" \
    IMAGE_BINARY="/usr/bin/sox" \
    IMAGE_TYPE="png" \
    IMAGE_THUMBNAIL_COMMAND="@BINARY@ --magic @INPUT@ -n spectrogram -r -x 225 -y 200 -o @OUTPUT@" \
    IMAGE_PREVIEW_COMMAND="@BINARY@ --magic @INPUT@ -n spectrogram -x 800 -Y 600 -o @OUTPUT@" \
    PREVIEW_BINARY="/usr/bin/sox" \
    PREVIEW_TYPE="mp3" \
    PREVIEW_COMMAND="@BINARY@ --magic @INPUT@ @OUTPUT@"

WORKDIR /extractor

RUN apk add --no-cache sox

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY binary_extractor.py extractor_info.json ./
CMD python binary_extractor.py
