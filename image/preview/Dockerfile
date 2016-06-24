# FROM clowder/python-base
FROM ncsa/clowder-extractors-python-base
MAINTAINER Rob Kooper <kooper@illinois.edu>


# Setup environment variables. These are passed into the container. You can change
# these to your setup. If RABBITMQ_URI is not set, it will try and use the rabbitmq
# server that is linked into the container. MAIN_SCRIPT is set to the script to be
# executed by entrypoint.sh
ENV RABBITMQ_URI="" \
    RABBITMQ_EXCHANGE="clowder" \
    RABBITMQ_VHOST="%2F" \
    RABBITMQ_QUEUE="ncsa.image.preview" \
    REGISTRATION_ENDPOINTS="https://clowder.ncsa.illinois.edu/extractors" \
    MAIN_SCRIPT="ncsa.image.preview.py" \
    THUMBNAIL_FLAGS="-resize 225^" \
    PREVIEW_FLAGS="-resize 800x600"

# Install any programs needed
USER root
RUN apt-get update && apt-get install -y \
       imagemagick \
       ufraw-batch \
    && rm -rf /var/lib/apt/lists/* \
    pip install --upgrade python-logstash  

# Switch to clowder, copy files and be ready to run
USER clowder

# command to run when starting docker
COPY entrypoint.sh *.py extractor_info.json /home/clowder/
ENTRYPOINT ["/home/clowder/entrypoint.sh"]
CMD ["extractor"]
