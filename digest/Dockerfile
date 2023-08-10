FROM python:3.7

ARG VERSION="unknown"
ARG BUILDNUMBER="unknown"
ARG GITSHA1="unknown"

# environemnt variables
ENV VERSION=${VERSION} \
    BUILDNUMBER=${BUILDNUMBER} \
    CLOWDER_VERSION=1 \
    GITSHA1=${GITSHA1} \
    STREAM=requests \
    RABBITMQ_QUEUE="ncsa.file.digest" \
    EXTRACTOR_HASHLIST="md5","sha1","sha224","sha256","sha384","sha512"

WORKDIR /extractor
COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY ncsa.file.digest.py extractor_info.json ./
CMD python ncsa.file.digest.py
