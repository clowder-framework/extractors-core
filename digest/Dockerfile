# ------------------------------------------------------------
# create requirements.txt
# ------------------------------------------------------------
FROM python:3.7 AS pipenv
RUN pip install pipenv
COPY Pipfile* /tmp/
RUN cd /tmp && pipenv lock --requirements > requirements.txt

# ------------------------------------------------------------
# build actual container
# ------------------------------------------------------------
FROM python:3-alpine

ENV EXTRACTOR_HASHLIST="md5","sha1","sha224","sha256","sha384","sha512"

# Install requirements
WORKDIR /home/clowder
COPY --from=pipenv /tmp/requirements.txt /home/clowder/
RUN pip install -r /home/clowder/requirements.txt

# Copy application
COPY *.py *.json /home/clowder/

# Start application
CMD python /home/clowder/ncsa.file.digest.py
