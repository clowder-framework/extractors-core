FROM python:3.11-alpine

# Install required packages
RUN apk add --no-cache \
    fuse \
    s3fs-fuse \
    curl    

# Create mount directory
RUN mkdir /clowderfs

# Create entrypoint script
# The script mounts the bucket using credentials passed as environment variables.
# It ensures that the MinIO container is ready before the mount.

COPY entrypoint.sh /entrypoint.sh

# # Make the script executable
RUN chmod +x /entrypoint.sh


# Set the entrypoint for the container
ENTRYPOINT ["/entrypoint.sh"]