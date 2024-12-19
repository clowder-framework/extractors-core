#!/bin/sh
set -e

# Ensure required environment variables are set
if [[ -z "${MINIO_ACCESS_KEY}" || -z "${MINIO_SECRET_KEY}" || -z "${MINIO_ENDPOINT}" ]]; then
    echo "ERROR: MINIO_ACCESS_KEY, MINIO_SECRET_KEY, and MINIO_ENDPOINT must be set."
    exit 1
fi

# Create credentials file using environment variables
echo "${MINIO_ACCESS_KEY}:${MINIO_SECRET_KEY}" > /.miniocred
chmod 600 /.miniocred

# Wait for the MinIO endpoint to become available
until curl -s "http://${MINIO_ENDPOINT}" >/dev/null; do
    echo "Waiting for MinIO at ${MINIO_ENDPOINT}..."
    sleep 3
done

# Mount the S3 bucket
s3fs clowder /clowderfs \
    -o passwd_file=/.miniocred \
    -o use_path_request_style \
    -o url=http://${MINIO_ENDPOINT}/ \
    -o allow_other

# Keep the container running
exec tail -f /dev/null

