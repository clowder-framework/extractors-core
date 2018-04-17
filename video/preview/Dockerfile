FROM clowder/extractors-binary-preview:onbuild

ENV RABBITMQ_QUEUE="ncsa.video.preview" \
    IMAGE_BINARY="/usr/bin/avconv" \
    IMAGE_TYPE="png" \
    IMAGE_THUMBNAIL_COMMAND="@BINARY@ -y -i @INPUT@ -ss 1 -t 1 -r 1 -vcodec png -f rawvideo -vf scale=225:-1 @OUTPUT@" \
    IMAGE_PREVIEW_COMMAND="@BINARY@ -y -i @INPUT@ -ss 1 -t 1 -r 1 -vcodec png -f rawvideo @OUTPUT@" \
    PREVIEW_BINARY="/usr/bin/avconv" \
    PREVIEW_TYPE="mp4" \
    PREVIEW_COMMAND="@BINARY@ -y -i @INPUT@ -c:v libx264 -profile:v baseline -preset slow -vf scale=-1:'if(gt(ih,360),360,ih)' -strict experimental -c:a aac -b:a 48k -movflags +faststart @OUTPUT@"
