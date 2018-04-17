FROM clowder/extractors-binary-preview:onbuild

ENV RABBITMQ_QUEUE="ncsa.pdf.preview" \
    IMAGE_BINARY="/usr/bin/convert" \
    IMAGE_TYPE="png" \
    IMAGE_THUMBNAIL_COMMAND="@BINARY@ @INPUT@[0] -density 300 -resize 225^ @OUTPUT@" \
    IMAGE_PREVIEW_COMMAND="@BINARY@ @INPUT@[0] -density 300 -resize 800x600 @OUTPUT@" \
    PREVIEW_BINARY="/bin/cp" \
    PREVIEW_TYPE="pdf" \
    PREVIEW_COMMAND="@BINARY@ @INPUT@ @OUTPUT@"
