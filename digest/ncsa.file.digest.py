#!/usr/bin/env python

import logging
import hashlib, zlib
import requests
import json

from pyclowder.extractors import Extractor
from pyclowder.utils import CheckMessage
import pyclowder.files


class FileDigestCalculator(Extractor):
    def __init__(self):
        Extractor.__init__(self)

        # add any additional arguments to parser
        # self.parser.add_argument('--max', '-m', type=int, nargs='?', default=-1,
        #                          help='maximum number (default=-1)')
        self.parser.add_argument('--hashes', dest="hash_list", type=str, nargs='?',
                                 default='["md5","sha1","sha224","sha256","sha384","sha512"]',
                                 help="list of hash types to calculate")

        # parse command line and load default logging configuration
        self.setup()

        # setup logging for the exctractor
        logging.getLogger('pyclowder').setLevel(logging.DEBUG)
        logging.getLogger('__main__').setLevel(logging.DEBUG)

        # assign other arguments
        self.hash_list = json.loads(self.args.hash_list)

    # Check whether dataset already has metadata
    def check_message(self, connector, host, secret_key, resource, parameters):
        return CheckMessage.bypass

    def process_message(self, connector, host, secret_key, resource, parameters):
        url = '%s/api/files/%s/blob?key=%s' % (host, resource['id'], secret_key)

        logging.debug("sending request for digest streaming: "+url)
        r = requests.get(url, stream=True)

        # Prepare hash objects
        hashes = {}
        for alg in self.hash_list:
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
        for alg in self.hash_list:
            hashContext[alg] = "http://www.w3.org/2001/04/xmldsig-more#%s" % alg

        # store results as metadata
        metadata = {
            "@context": ["https://clowder.ncsa.illinois.edu/contexts/metadata.jsonld", hashContext],
            "dataset_id": resource['parent'].get('id', None),
            "content": hashDigest,
            "agent": {
                "@type": "cat:extractor",
                "extractor_id": host + "/api/extractors/" + self.extractor_info['name']
            }
        }

        pyclowder.files.upload_metadata(connector, host, secret_key, resource['id'], metadata)

if __name__ == "__main__":
    extractor = FileDigestCalculator()
    extractor.start()
