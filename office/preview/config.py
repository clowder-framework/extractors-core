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
extractorName = os.getenv('RABBITMQ_QUEUE', "ncsa.office.preview")

# URL to be used for connecting to rabbitmq
rabbitmqURL = os.getenv('RABBITMQ_URI', "amqp://guest:guest@localhost/%2f")

# name of rabbitmq exchange
rabbitmqExchange = os.getenv('RABBITMQ_EXCHANGE', "clowder")

# type of files to process
messageType = ["*.file.application.msword.#",
               "*.file.application.excel.#",
               "*.file.application.vnd_openxmlformats-officedocument_wordprocessingml_document.#",
               "*.file.application.vnd_openxmlformats-officedocument_spreadsheetml_sheet.#",
               "*.file.application.vnd_openxmlformats-officedocument_presentationml_presentation.#",
               "*.file.application.vnd_openxmlformats-officedocument_presentationml_slideshow.#",
               "*.file.application.vnd_ms-word_document_macroEnabled_12.#",
               "*.file.application.vnd_ms-excel.#",
               "*.file.application.vnd_ms-excel_sheet_macroEnabled_12.#",
               "*.file.application.vnd_ms-excel_addin_macroEnabled_12.#",
               "*.file.application.vnd_ms-excel_sheet_binary_macroEnabled_12.#",
               "*.file.application.vnd_ms-powerpoint.#",
               "*.file.application.vnd_ms-powerpoint_addin_macroEnabled_12.#",
               "*.file.application.vnd_ms-powerpoint_presentation_macroEnabled_12.#",
               "*.file.application.vnd_ms-powerpoint_slideshow_macroEnabled_12.#",
               "*.file.application.vnd_oasis_opendocument_text.#",
               "*.file.application.vnd_oasis_opendocument_text-template.#",
               "*.file.application.vnd_oasis_opendocument_text-web.#",
               "*.file.application.vnd_oasis_opendocument_text-master.#",
               "*.file.application.vnd_oasis_opendocument_graphics.#",
               "*.file.application.vnd_oasis_opendocument_graphics-template.#",
               "*.file.application.vnd_oasis_opendocument_presentation.#",
               "*.file.application.vnd_oasis_opendocument_presentation-template.#",
               "*.file.application.vnd_oasis_opendocument_spreadsheet.#",
               "*.file.application.vnd_oasis_opendocument_spreadsheet-template.#",
               "*.file.application.vnd_oasis_opendocument_chart.#",
               "*.file.application.vnd_oasis_opendocument_formula.#",
               "*.file.application.vnd_oasis_opendocument_database.#",
               "*.file.application.vnd_oasis_opendocument_image.#"]

# trust certificates, set this to false for self signed certificates
sslVerify = os.getenv('RABBITMQ_SSLVERIFY', False)

# Comma delimited list of endpoints and keys for registering extractor information
registrationEndpoints = os.getenv('REGISTRATION_ENDPOINTS', "http://localhost:9000/clowder/api/extractors?key=key1, http://host2:9000/api/extractors?key=key2")

# type specific preview
libreoffice = "/usr/bin/libreoffice"

# type preview command line
libreofficeCommand = "@BINARY@ --headless --convert-to pdf @INPUT@"

# image generating binary, or None if none is to be generated
convert = "/usr/bin/convert"

# image thumbnail command line
convertCommand = "@BINARY@ @INPUT@[0] -density 300 -resize 225^ @OUTPUT@"
