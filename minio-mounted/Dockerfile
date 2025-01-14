FROM python:3.10

# Install required packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    fuse \
    s3fs \
    curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Create mount directory
RUN mkdir /clowderfs

# Create entrypoint script
# The script mounts the bucket using credentials passed as environment variables.
# It ensures that the MinIO container is ready before the mount.

COPY entrypoint.sh /entrypoint.sh

# # Make the script executable
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

