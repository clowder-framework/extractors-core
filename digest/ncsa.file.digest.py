#!/usr/bin/env python

import hashlib
import logging
import os
import requests

from pyclowder.extractors import Extractor
from pyclowder.utils import CheckMessage
import pyclowder.files


class FileDigestCalculator(Extractor):
    def __init__(self):
        Extractor.__init__(self)

        hashes = os.getenv('EXTRACTOR_HASHLIST', "md5,sha1,sha224,sha256,sha384,sha512")

        # add any additional arguments to parser
        self.parser.add_argument('--hashes', dest="hash_list", type=str, nargs='?', default=hashes,
                                 help="list of hash types to calculate")

        # parse command line and load default logging configuration
        self.setup()

        # setup logging for the exctractor
        logging.getLogger('pyclowder').setLevel(logging.DEBUG)
        logging.getLogger('__main__').setLevel(logging.DEBUG)

        # assign other arguments
        self.hash_list = [x.strip() for x in self.args.hash_list.split(',')]

    # Check whether dataset already has metadata
    def check_message(self, connector, host, secret_key, resource, parameters):
        return CheckMessage.bypass

    def process_message(self, connector, host, secret_key, resource, parameters):
        logger = logging.getLogger('__main__')
        url = '%sapi/files/%s/blob?key=%s' % (host, resource['id'], secret_key)

        logger.debug("sending request for digest streaming: "+url)
        r = requests.get(url, stream=True)

        # Prepare hash objects
        hashes = {}
        for alg in self.hash_list:
            hashes[alg] = hashlib.new(alg)

        # Stream file and update hashes
        for chunk in r.iter_content():
            for hash in hashes.values():
                hash.update(chunk)

        # Generate final hex hash
        hash_digest = {}
        for (k, v) in hashes.items():
            hash_digest[k] = v.hexdigest()

        # Generate JSON-LD context
        hash_context = {}
        for alg in self.hash_list:
            hash_context[alg] = "http://www.w3.org/2001/04/xmldsig-more#%s" % alg

        # store results as metadata
        metadata = {
            "@context": ["https://clowder.ncsa.illinois.edu/contexts/metadata.jsonld", hash_context],
            "dataset_id": resource['parent'].get('id', None),
            "content": hash_digest,
            "agent": {
                "@type": "cat:extractor",
                "extractor_id": host + "api/extractors/" + self.extractor_info['name']
            }
        }

        pyclowder.files.upload_metadata(connector, host, secret_key, resource['id'], metadata)


if __name__ == "__main__":
    extractor = FileDigestCalculator()
    extractor.start()
