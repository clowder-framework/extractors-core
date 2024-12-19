# Minio-mounted extractors

This is a DinD (Docker in Docker) setup that mounts a Minio bucket to the host filesystem and runs extractors on the data in the bucket.

## How to run
This docker image requires privileged mode to run. We also need to set up environment variables for the Minio server and the bucket name. To run in the clowder2 docker-compose, this is the setup

```yaml
  minio-mounted-extractor:
    image: minio-mounted-extractor
    networks:
      - clowder2
    restart: unless-stopped
    environment:
      MINIO_ENDPOINT: minio-nginx:9000
      MINIO_ACCESS_KEY: minioadmin
      MINIO_SECRET_KEY: minioadmin
    # Added privileged mode and device mappings for FUSE support
    privileged: true
    devices:
      - /dev/fuse:/dev/fuse
    cap_add:
      - SYS_ADMIN
    security_opt:
      - apparmor:unconfined
    depends_on:
      - minio-nginx
```