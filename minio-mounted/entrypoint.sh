#!/bin/sh

set -e

# Ensure required environment variables are set
if [ -z "${MINIO_ACCESS_KEY}" ] || [ -z "${MINIO_SECRET_KEY}" ] || [ -z "${MINIO_ENDPOINT}" ]; then
    echo "ERROR: MINIO_ACCESS_KEY, MINIO_SECRET_KEY, and MINIO_ENDPOINT must be set."
    exit 1
fi

# Create credentials file using environment variables
echo "${MINIO_ACCESS_KEY}:${MINIO_SECRET_KEY}" > /.miniocred
chmod 600 /.miniocred

# Set a timeout for waiting for the MinIO endpoint (in seconds)
TIMEOUT=60
START_TIME=$(date +%s)

check_minio() {
    # Try to access MinIO's health endpoint
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "${MINIO_ENDPOINT}/minio/health/live")
    
    # Also acceptable are 403 (Forbidden) and 401 (Unauthorized) as they indicate MinIO is running
    if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "403" ] || [ "$HTTP_CODE" = "401" ]; then
        return 0
    fi
    return 1
}

until check_minio; do
    ELAPSED_TIME=$(( $(date +%s) - START_TIME ))
    if [ "$ELAPSED_TIME" -ge "$TIMEOUT" ]; then
        echo "ERROR: Timeout reached while waiting for MinIO at ${MINIO_ENDPOINT}."
        exit 1
    fi
    
    echo "Waiting for MinIO at ${MINIO_ENDPOINT}... (${ELAPSED_TIME}s elapsed)"
    sleep 3
done

echo "MinIO endpoint is responding!"

# Mount the S3 bucket
s3fs clowder /clowderfs \
    -o passwd_file=/.miniocred \
    -o use_path_request_style \
    -o url=${MINIO_ENDPOINT}/ \
    -o allow_other

# Wait a moment for the mount to be ready
sleep 2

# Execute the command passed to the container
echo "Mount complete, executing command: $@"
exec "$@"