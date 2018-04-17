FROM clowder/extractors-binary-preview:onbuild

ENV RABBITMQ_QUEUE="ncsa.image.preview" \
    IMAGE_BINARY="/usr/bin/convert" \
    IMAGE_TYPE="png" \
    IMAGE_THUMBNAIL_COMMAND="@BINARY@ @INPUT@ -resize 225^ @OUTPUT@" \
    IMAGE_PREVIEW_COMMAND="@BINARY@ @INPUT@ -resize 800x600 @OUTPUT@"
