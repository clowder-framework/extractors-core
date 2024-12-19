# Minio-mounted extractors

This is a DinD (Docker in Docker) setup that mounts a Minio bucket to the host filesystem and runs extractors on the data in the bucket.

## How to run
This docker image requires privileged mode to run. We also need to set up environment variables for the Minio server and the bucket name. To run in the clowder2 docker-compose, this is the setup

```yaml
  minio-mounted-dind:
    image: minio-mounted-dind
    networks:
      - clowder2
    restart: unless-stopped
    ports:
      - 2376:2376
    environment:
      MINIO_ENDPOINT: minio-nginx:9000
      MINIO_ACCESS_KEY: minioadmin
      MINIO_SECRET_KEY: minioadmin
    volumes:
      - dind-storage:/var/lib/docker
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

Sources:
- [docker-s3fs-client](https://github.com/efrecon/docker-s3fs-client/blob/master/docker-compose.yml)