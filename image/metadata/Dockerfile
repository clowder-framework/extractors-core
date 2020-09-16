FROM python:3.7-alpine

ENV RABBITMQ_QUEUE="ncsa.image.metadata" \
    IMAGE_BINARY="/usr/bin/identify"

WORKDIR /extractor

RUN apk add --no-cache imagemagick

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY ncsa.image.metadata.py extractor_info.json ./
CMD python ncsa.image.metadata.py
