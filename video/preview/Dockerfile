FROM python:3.7-alpine

ARG VERSION="unknown"
ARG BUILDNUMBER="unknown"
ARG GITSHA1="unknown"

# environemnt variables
ENV VERSION=${VERSION} \
    BUILDNUMBER=${BUILDNUMBER} \
    GITSHA1=${GITSHA1} \
    RABBITMQ_QUEUE="ncsa.video.preview" \
    IMAGE_BINARY="/usr/bin/avconv" \
    IMAGE_TYPE="png" \
    IMAGE_THUMBNAIL_COMMAND="@BINARY@ -y -i @INPUT@ -ss 1 -t 1 -r 1 -vcodec png -f rawvideo -vf scale=225:-1 @OUTPUT@" \
    IMAGE_PREVIEW_COMMAND="@BINARY@ -y -i @INPUT@ -ss 1 -t 1 -r 1 -vcodec png -f rawvideo @OUTPUT@" \
    PREVIEW_BINARY="/usr/bin/ffmpeg" \
    PREVIEW_TYPE="mp4" \
    PREVIEW_COMMAND="@BINARY@ -y -i @INPUT@ -c:v libx264 -profile:v baseline -preset slow -vf scale=-1:'min(ih,360)' -strict experimental -c:a aac -b:a 48k -movflags +faststart @OUTPUT@"

WORKDIR /extractor

RUN apk add --no-cache ffmpeg

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY binary_extractor.py extractor_info.json ./
CMD python binary_extractor.py
