FROM python:3.7

ARG VERSION="unknown"
ARG BUILDNUMBER="unknown"
ARG GITSHA1="unknown"

# environemnt variables
ENV VERSION=${VERSION} \
    BUILDNUMBER=${BUILDNUMBER} \
    GITSHA1=${GITSHA1} \
    CLOWDER_VERSION=1 \
    RABBITMQ_QUEUE="ncsa.image.preview" \
    IMAGE_BINARY="/usr/bin/convert" \
    IMAGE_TYPE="png" \
    IMAGE_RESOURCE_MEMORY="4Gib" \
    IMAGE_RESOURCE_DISK="10Gib" \
    IMAGE_RESOURCE_PIXELS="50KP" \
    IMAGE_THUMBNAIL_COMMAND="@BINARY@ @INPUT@[0] -auto-orient -resize 225^ @OUTPUT@" \
    IMAGE_PREVIEW_COMMAND="@BINARY@ @INPUT@[0] -auto-orient -resize 800x600 @OUTPUT@" \
    MAGICK_CONFIGURE_PATH='/extractor'

WORKDIR /extractor

RUN apt update && apt-get install -y build-essential imagemagick

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY binary_extractor.py extractor_info.json entrypoint.sh ./

ENTRYPOINT ["/extractor/entrypoint.sh"]
CMD ["extractor"]
