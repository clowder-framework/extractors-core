# FROM clowder/python-base
FROM maven:3-onbuild
MAINTAINER Marcus Slavenas <slavenas@illinois.edu>

# Install any programs needed
# USER root
# RUN apt-get update && apt-get install -y \
#        imagemagick \
#     && rm -rf /var/lib/apt/lists/*   

# Switch to clowder, copy files and be ready to run
USER clowder

# command to run when starting docker
CMD ["mvn exec:java -Dexec.mainClass="edu.illinois.ncsa.medici.extractor.ExtractText"]  

# Setup environment variables. These are passed into the container. You can change
# these to your setup. If RABBITMQ_URI is not set, it will try and use the rabbitmq
# server that is linked into the container.
ENV RABBITMQ_URI="" \
    RABBITMQ_EXCHANGE="clowder" \
    RABBITMQ_VHOST="%2F" \
    RABBITMQ_QUEUE="speech2text"
