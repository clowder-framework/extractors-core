#!/usr/bin/env python

import logging
import os
import subprocess
import tempfile
import re
from config import *
import pyclowder.extractors as extractors


def main():
    global extractorName, messageType, rabbitmqExchange, rabbitmqURL, logger, registrationEndpoints

    # set logging
    logging.basicConfig(format='%(asctime)-15s %(levelname)-7s : %(name)s - %(message)s', level=logging.INFO)
    logging.getLogger('pyclowder.extractors').setLevel(logging.DEBUG)
    logger = logging.getLogger(extractorName)
    logger.setLevel(logging.DEBUG)

    # setup
    extractors.setup(extractorName=extractorName,
                       messageType=messageType,
                       rabbitmqURL=rabbitmqURL,
                       rabbitmqExchange=rabbitmqExchange)

    # register extractor info
    extractors.register_extractor(registrationEndpoints)

    # connect to rabbitmq
    extractors.connect_message_bus(extractorName=extractorName,
                                   messageType=messageType,
                                   processFileFunction=process_file,
                                   rabbitmqExchange=rabbitmqExchange,
                                   rabbitmqURL=rabbitmqURL)

# ----------------------------------------------------------------------
# Process the file and upload the results


def process_file(parameters):
    global imageBinary, imageType, imageThumbnail, imagePreview
    global previewBinary, previewType, previewCommand

    if imageBinary:
        execute_command(parameters, imageBinary, imageThumbnail, imageType, True)
        execute_command(parameters, imageBinary, imagePreview, imageType, False)
    if previewBinary:
        execute_command(parameters, previewBinary, previewCommand, previewType, False)


def execute_command(parameters, binary, commandline, ext, thumbnail=False):
    global logger

    (fd, tmpfile) = tempfile.mkstemp(suffix='.' + ext)
    try:
        # close tempfile
        os.close(fd)

        # replace some special tokens
        commandline = commandline.replace('@BINARY@', binary)
        commandline = commandline.replace('@INPUT@', parameters['inputfile'])
        commandline = commandline.replace('@OUTPUT@', tmpfile)

        # split command line
        p = re.compile(r'''((?:[^ "']|"[^"]*"|'[^']*')+)''')
        commandline = p.split(commandline)[1::2]

        # execute command
        x = subprocess.check_output(commandline, stderr=subprocess.STDOUT)
        if x:
            logger.debug(binary + " : " + x)

        if(os.path.getsize(tmpfile) != 0):
            # upload result
            if thumbnail:
                extractors.upload_thumbnail(thumbnail=tmpfile, parameters=parameters)
                extractors.status_update(channel=parameters['channel'], header=parameters['header'],
                                         fileid=parameters['fileid'], status="Uploaded thumbnail")
            else:
                extractors.upload_preview(previewfile=tmpfile, parameters=parameters)
                extractors.status_update(channel=parameters['channel'], header=parameters['header'],
                                         fileid=parameters['fileid'], status="Uploaded preview")
        else:
            msg = "Extraction resulted in 0 byte file, nothing uploaded."
            extractors.status_update(channel=parameters['channel'], header=parameters['header'],
                                     fileid=parameters['fileid'], status=msg)
            logger.warn(msg)

    except subprocess.CalledProcessError as e:
        msg = "ERROR [%d] : %s" % (e.returncode, e.message)
        extractors.status_update(channel=parameters['channel'], header=parameters['header'], fileid=parameters['fileid'], status=msg)
        logger.exception(msg)
        raise
    finally:
        try:
            os.remove(tmpfile)
        except:
            pass

if __name__ == "__main__":
    main()
