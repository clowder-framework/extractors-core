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
    global libreoffice, libreofficeCommand, convert, convertCommand

    inputfile = parameters['inputfile']
    pdffile   = re.sub(r"\..*$", ".pdf", inputfile)
    pngfile   = re.sub(r"\..*$", ".png", inputfile)

    try:
        execute_command(parameters, libreoffice, libreofficeCommand, inputfile, pdffile, False)
        execute_command(parameters, convert, convertCommand, pdffile, pngfile, True)
    finally:
        try:
            if os.path.isfile(pngfile):
                os.remove(pngfile)
        except:
            logger.error("could not remove png file : " + str(e.output))
            pass
        try:
            if os.path.isfile(pdffile):
                os.remove(pdffile)
        except:
            logger.error("could not remove pdf file : " + str(e.output))
            pass


def execute_command(parameters, binary, commandline, inputfile, outputfile, thumbnail=False):
    global logger

    try:
        # replace some special tokens
        commandline = commandline.replace('@BINARY@', binary)
        commandline = commandline.replace('@INPUT@', inputfile)
        commandline = commandline.replace('@OUTPUT@', outputfile)
        logger.debug(commandline)

        # split command line
        p = re.compile(r'''((?:[^ "']|"[^"]*"|'[^']*')+)''')
        commandline = p.split(commandline)[1::2]

        # execute command
        x = subprocess.check_output(commandline, stderr=subprocess.STDOUT, cwd=os.path.dirname(inputfile))
        if x:
            logger.debug(binary + " : " + x)

        if os.path.isfile(outputfile) and os.path.getsize(outputfile) != 0:
            # upload result
            if thumbnail:
                extractors.upload_thumbnail(thumbnail=outputfile, parameters=parameters)
            else:
                extractors.upload_preview(previewfile=outputfile, parameters=parameters)
        else:
            log.warn("Extraction resulted in 0 byte file, nothing uploaded.")

    except subprocess.CalledProcessError as e:
        logger.error(binary + " : " + str(e.output))
        raise

if __name__ == "__main__":
    main()
