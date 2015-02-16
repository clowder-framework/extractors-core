#!/usr/bin/env python

import pika
import requests
import sys
import time
import json
import subprocess
import tempfile
import os
import logging
from config import *
import pymedici.extractors as extractors

def main():
  global extractorName, messageType, rabbitmqExchange, rabbitmqURL    

  #set logging
  logging.basicConfig(format='%(levelname)-7s : %(name)s -  %(message)s', level=logging.WARN)
  logging.getLogger('pymedici.extractors').setLevel(logging.INFO)

  #connect to rabbitmq
  extractors.connect_message_bus(extractorName=extractorName, messageType=messageType, processFileFunction=process_file, 
      rabbitmqExchange=rabbitmqExchange, rabbitmqURL=rabbitmqURL)

# ----------------------------------------------------------------------
# Process the file and upload the results
def process_file(parameters):
    global extractorName, convertexe, imagetype, size
    global logger

    (fd, thumbnailfile)=tempfile.mkstemp(suffix='.' + imagetype)
    try:
      # convert image to right size
      #args = [['convert', inputfile, '-resize', size], args, [thumbnailfile]]
      #subprocess.check_output(list(itertools.chain(*args)), stderr=subprocess.STDOUT)
      subprocess.check_output([convertexe,  inputfile, '-resize', size, thumbnailfile], stderr=subprocess.STDOUT)

      if(os.path.getsize(thumbnailfile) == 0):
        raise Exception("File is empty.")

      # upload preview image
      extractors.upload_file_metadata(previewfile=thumbnailfile, parameters=parameters)
    finally:
      try:
        os.remove(thumbnailfile)
      except:
        pass    

if __name__ == "__main__":
    main()

