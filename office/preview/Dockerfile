FROM clowder/pyclowder:onbuild

ENV MAIN_SCRIPT="ncsa.office.preview.py" \
    RABBITMQ_QUEUE="ncsa.office.preview" \
    IMAGE_BINARY="/usr/bin/convert" \
    IMAGE_TYPE="png" \
    IMAGE_THUMBNAIL_COMMAND="@BINARY@ @INPUT@[0] -density 300 -resize 225^ @OUTPUT@" \
    IMAGE_PREVIEW_COMMAND="" \
    PREVIEW_BINARY="/usr/bin/libreoffice" \
    PREVIEW_TYPE="pdf" \
    PREVIEW_COMMAND="@BINARY@ --headless --convert-to pdf @INPUT@"
