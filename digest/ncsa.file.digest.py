#!/usr/bin/env python

import logging
import os
import subprocess
import tempfile
import re
import hashlib, zlib
import requests
from config import *
import pyclowder.extractors as extractors


def main():
    global extractorName, messageType, rabbitmqExchange, rabbitmqURL, logger

    # set logging
    logging.basicConfig(format='%(asctime)-15s %(levelname)-7s : %(name)s - %(message)s', level=logging.INFO)
    logging.getLogger('pyclowder.extractors').setLevel(logging.DEBUG)
    logger = logging.getLogger(extractorName)
    logger.setLevel(logging.DEBUG)

    # connect to rabbitmq
    extractors.connect_message_bus(extractorName=extractorName,
                                   messageType=messageType,
                                   processFileFunction=process_file,
                                   rabbitmqExchange=rabbitmqExchange,
                                   rabbitmqURL=rabbitmqURL,
                                   checkMessageFunction=check_message)



# ----------------------------------------------------------------------
# We will stream the file ourselves here, instead of returning True and downloading to process_file()
def check_message(parameters):
    print(parameters)

    # Prepare target URL
    fileTarget = parameters['host']
    fileTarget += "/" if fileTarget[0] != "/" else ""
    fileTarget += "api/files/%s/blob?key=%s" % (parameters['id'], parameters['secretKey'])

    logger.debug("sending request for digest streaming: "+fileTarget)
    r = requests.get(fileTarget, stream=True)

    if hashList["md5"]: md5 = hashlib.md5()
    if hashList["sha1"]: sha1 = hashlib.sha1()
    if hashList["sha224"]: sha224 = hashlib.sha224()
    if hashList["sha256"]: sha256 = hashlib.sha256()
    if hashList["sha384"]: sha384 = hashlib.sha384()
    if hashList["sha512"]: sha512 = hashlib.sha512()

    for chunk in r.iter_content():
        if hashList["md5"]: md5.update(chunk)
        if hashList["sha1"]: sha1.update(chunk)
        if hashList["sha224"]: sha224.update(chunk)
        if hashList["sha256"]: sha256.update(chunk)
        if hashList["sha384"]: sha384.update(chunk)
        if hashList["sha512"]: sha512.update(chunk)

    # store results as metadata
    metadata = {
        "@context": {
            "@vocab": "https://tools.ietf.org/html/draft-eastlake-xmldsig-uri-00"
        },
        "dataset_id": parameters["datasetId"],
        "content": {
            "md5": md5.hexdigest(),
            "sha1": sha1.hexdigest(),
            "sha224": sha224.hexdigest(),
            "sha256": sha256.hexdigest(),
            "sha384": sha384.hexdigest(),
            "sha512": sha512.hexdigest()
        },
        "agent": {
            "@type": "cat:extractor",
            "extractor_id": parameters['host'] + "/api/extractors/" + extractorName
        }
    }

    extractors.upload_file_metadata_jsonld(mdata=metadata, parameters=parameters)
    return False

def process_file(parameters):
    pass

if __name__ == "__main__":
    main()
