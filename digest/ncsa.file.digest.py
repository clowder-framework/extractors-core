#!/usr/bin/env python

import hashlib
import logging
import os

import certifi
import pyclowder.files
import pycurl
import requests
from pyclowder.extractors import Extractor
from pyclowder.utils import CheckMessage


class FileDigestCalculator(Extractor):
    def __init__(self):
        Extractor.__init__(self)

        hashes = os.getenv('EXTRACTOR_HASHLIST', "md5,sha1,sha224,sha256,sha384,sha512")

        # add any additional arguments to parser
        self.parser.add_argument('--hashes', dest="hash_list", type=str, nargs='?', default=hashes,
                                 help="list of hash types to calculate")

        # parse command line and load default logging configuration
        self.setup()

        # setup logging for the extractor
        logging.getLogger('pyclowder').setLevel(logging.DEBUG)
        logging.getLogger('__main__').setLevel(logging.DEBUG)

        # assign other arguments
        self.hash_list = [x.strip() for x in self.args.hash_list.split(',')]

    # Check whether dataset already has metadata
    def check_message(self, connector, host, secret_key, resource, parameters):
        return CheckMessage.bypass

    def stream_requests(self, connector, url, hashes):
        # Stream file and update hashes
        r = requests.get(url, stream=True, verify=connector.ssl_verify if connector else True)
        for chunk in r.iter_content(chunk_size=10240):
            for hash_value in hashes.values():
                hash_value.update(chunk)

    def stream_pycurl(self, connector, url, hashes):
        def hash_data(data):
            for hash_value in hashes.values():
                hash_value.update(data)

        c = pycurl.Curl()
        if (connector and not connector.ssl_verify) or (os.getenv("SSL_IGNORE", "").lower() == "true"):
            c.setopt(pycurl.SSL_VERIFYPEER, 0)
            c.setopt(pycurl.SSL_VERIFYHOST, 0)
        c.setopt(c.URL, url)
        c.setopt(c.WRITEFUNCTION, hash_data)
        c.setopt(c.CAINFO, certifi.where())
        c.perform()
        c.close()

    def process_message(self, connector, host, secret_key, resource, parameters):
        logger = logging.getLogger('__main__')
        file_id = resource['id']
        url = '%sapi/files/%s/blob?key=%s&tracking=false' % (host, file_id, secret_key)

        # Prepare hash objects
        hashes = {}
        for alg in self.hash_list:
            hashes[alg] = hashlib.new(alg)

        # stream data and compute hash
        logger.debug("sending request for digest streaming: " + url)
        if os.getenv('STREAM', '').lower() == 'pycurl':
            self.stream_pycurl(connector, url, hashes)
        else:
            self.stream_requests(connector, url, hashes)

        # Generate final hex hash
        hash_digest = {}
        for (k, v) in hashes.items():
            hash_digest[k] = v.hexdigest()

        # Generate JSON-LD context
        hash_context = {}
        for alg in self.hash_list:
            hash_context[alg] = "http://www.w3.org/2001/04/xmldsig-more#%s" % alg

        # store results as metadata
        metadata = self.get_metadata(hash_digest, 'file', file_id, host)
        pyclowder.files.upload_metadata(connector, host, secret_key, file_id, metadata)


if __name__ == "__main__":
    extractor = FileDigestCalculator()
    extractor.start()
