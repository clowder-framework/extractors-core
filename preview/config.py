# =============================================================================
#
# In order for this extractor to run according to your preferences, 
# the following parameters need to be set. 
# 
# Some parameters can be left with the default values provided here - in that 
# case it is important to verify that the default value is appropriate to 
# your system. It is especially important to verify that paths to files and 
# software applications are valid in your system.
#
# =============================================================================

import os

# name to show in rabbitmq queue list
extractorName = os.getenv('RABBITMQ_QUEUE', "ncsa.video.preview")

# URL to be used for connecting to rabbitmq
rabbitmqURL = os.getenv('RABBITMQ_URI', "amqp://guest:guest@localhost/%2f")

# name of rabbitmq exchange
rabbitmqExchange = os.getenv('RABBITMQ_EXCHANGE', "clowder")

# type of files to process
messageType = "*.file.video.#"

# trust certificates, set this to false for self signed certificates
sslVerify = os.getenv('RABBITMQ_SSLVERIFY', False)

# image generating binary, or None if none is to be generated
imageBinary = "/usr/bin/avconv"

# image preview type
imageType = "png"

# image thumbnail command line
imageThumbnail = "@BINARY@ -y -i @INPUT@ -ss 1 -t 1 -r 1 -vcodec " + imageType + " -f rawvideo -vf scale=225:-1 @OUTPUT@"

# image preview command line
imagePreview = "@BINARY@ -y -i @INPUT@ -ss 1 -t 1 -r 1 -vcodec " + imageType + " -f rawvideo -vf scale='if(gt(iw,800),800,iw)':-1 @OUTPUT@"

# type specific preview, or None if none is to be generated
previewBinary = "/usr/bin/avconv"

# type preview type
previewType = "mp4"

# type preview command line
previewCommand = "@BINARY@ -y -i @INPUT@ -c:v libx264 -profile:v baseline -preset slow -vf scale=-1:'if(gt(ih,360),360,ih)' -strict experimental -c:a aac -b:a 48k -movflags +faststart @OUTPUT@"
