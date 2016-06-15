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
    global extractorName, messageType, rabbitmqExchange, rabbitmqURL, logger, hashList

    # set logging
    logging.basicConfig(format='%(asctime)-15s %(levelname)-7s : %(name)s - %(message)s', level=logging.INFO)
    logging.getLogger('pyclowder.extractors').setLevel(logging.DEBUG)
    logger = logging.getLogger(extractorName)
    logger.setLevel(logging.DEBUG)

    if isinstance(hashList,str):
        hashList = hashList.replace("[","").replace("]","").replace("'","").split(",")

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
    # Bypass downloading of this file for process_file() - we'll handle streaming it ourselves
    return "bypass"

def process_file(parameters):
    # Prepare target URL
    fileTarget = parameters['host']
    fileTarget += "/" if fileTarget[0] != "/" else ""
    fileTarget += "api/files/%s/blob?key=%s" % (parameters['id'], parameters['secretKey'])

    logger.debug("sending request for digest streaming: "+fileTarget)
    r = requests.get(fileTarget, stream=True)

    # Prepare hash objects
    hashes = {}
    for alg in hashList:
        hashes[alg] = hashlib.new(alg)

    # Stream file and update hashes
    for chunk in r.iter_content():
        for hash in hashes.itervalues():
            hash.update(chunk)

    # Generate final hex hash
    hashDigest = {}
    for (k,v) in hashes.iteritems():
        hashDigest[k] = v.hexdigest()

    # Generate JSON-LD context
    hashContext = {}
    for alg in hashList:
        hashContext[alg] = "http://www.w3.org/2001/04/xmldsig-more#%s" % alg

    # store results as metadata
    metadata = {
        "@context": hashContext,
        "dataset_id": parameters["datasetId"],
        "content": hashDigest,
        "agent": {
            "@type": "cat:extractor",
            "extractor_id": parameters['host'] + "/api/extractors/" + extractorName
        }
    }

    extractors.upload_file_metadata_jsonld(mdata=metadata, parameters=parameters)

if __name__ == "__main__":
    main()
