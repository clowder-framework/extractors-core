#!/usr/bin/env python
import logging
import tempfile

import pyclowder
from pyclowder.extractors import Extractor


class TextPreviewExtractor(Extractor):

    def __init__(self):
        Extractor.__init__(self)
        self.setup()

        # setup logging for the extractor
        logging.getLogger('pyclowder').setLevel(logging.DEBUG)
        logging.getLogger('__main__').setLevel(logging.DEBUG)

    def process_message(self, connector, host, secret_key, resource, parameters):
        # Process the file and upload the results

        inputfile = resource["local_paths"][0]
        file_id = resource['id']

        # 1 MB
        num_bytes = 1000000

        with open(inputfile, 'r') as file:
            lines = file.readlines(num_bytes)
            tmp = tempfile.NamedTemporaryFile(suffix=".txt", mode="w", delete=False, dir='./')
            tmp.write("Previewing up to the first 1 megabyte of file contents. Download file to see full data.\n---\n")
            for line in lines:
                tmp.write(line)
            tmp.close()

        pyclowder.files.upload_preview(connector, host, secret_key, file_id, tmp.name, None)
        connector.status_update(pyclowder.utils.StatusMessage.processing, resource,
                                "Uploaded preview of type txt")


if __name__ == "__main__":
    extractor = TextPreviewExtractor()
    extractor.start()
