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
extractorName = os.getenv('RABBITMQ_QUEUE', "ncsa.audio.preview")

# URL to be used for connecting to rabbitmq
rabbitmqURL = os.getenv('RABBITMQ_URI', "amqp://guest:guest@localhost/%2f")

# name of rabbitmq exchange
rabbitmqExchange = os.getenv('RABBITMQ_EXCHANGE', "clowder")

# type of files to process
messageType = "*.file.audio.#"

# trust certificates, set this to false for self signed certificates
sslVerify = os.getenv('RABBITMQ_SSLVERIFY', False)

# image generating binary, or None if none is to be generated
imageBinary = "/usr/bin/sox"

# image preview type
imageType = "png"

# image thumbnail command line
imageThumbnail = "@BINARY@ --magic @INPUT@ -n spectrogram -r -x 225 -y 200 -o @OUTPUT@"

# image preview command line
imagePreview = "@BINARY@ --magic @INPUT@ -n spectrogram -x 800 -Y 600 -o @OUTPUT@"

# type specific preview, or None if none is to be generated
previewBinary = "/usr/bin/sox"

# type preview type
previewType = "mp3"

# type preview command line
previewCommand = "@BINARY@ --magic @INPUT@ @OUTPUT@"
