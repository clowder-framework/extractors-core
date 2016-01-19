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
extractorName = os.getenv('RABBITMQ_QUEUE', "ncsa.pdf.preview")

# URL to be used for connecting to rabbitmq
rabbitmqURL = os.getenv('RABBITMQ_URI', "amqp://guest:guest@localhost/%2f")

# name of rabbitmq exchange
rabbitmqExchange = os.getenv('RABBITMQ_EXCHANGE', "clowder")

# type of files to process
messageType = "*.file.application.pdf.#"

# trust certificates, set this to false for self signed certificates
sslVerify = os.getenv('RABBITMQ_SSLVERIFY', False)

# image generating binary, or None if none is to be generated
imageBinary = "/usr/local/bin/convert"

# image preview type
imageType = "png"

# image thumbnail command line
imageThumbnail = "@BINARY@ @INPUT@[0] -density 300 -resize 225^ @OUTPUT@"

# image preview command line
imagePreview = "@BINARY@ @INPUT@[0] -density 300 -resize 800x600 @OUTPUT@"

# type specific preview, or None if none is to be generated
previewBinary = "/bin/cp"

# type preview type
previewType = "pdf"

# type preview command line
previewCommand = "@BINARY@ @INPUT@ @OUTPUT@"
