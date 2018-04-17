#!/usr/bin/env python

import logging
import os
import re
import subprocess
import tempfile

from pyclowder.extractors import Extractor
import pyclowder.files
import pyclowder.utils


class OfficePreviewExtractor(Extractor):
    """Count the number of characters, words and lines in a text file."""
    def __init__(self):
        Extractor.__init__(self)

        image_binary = os.getenv('IMAGE_BINARY', '')
        image_type = os.getenv('IMAGE_TYPE', 'png')
        image_thumbnail_command = os.getenv('IMAGE_THUMBNAIL_COMMAND', '@BINARY@ @INPUT@ @OUTPUT@')
        image_preview_command = os.getenv('IMAGE_PREVIEW_COMMAND', '@BINARY@ @INPUT@ @OUTPUT@')
        preview_binary = os.getenv('PREVIEW_BINARY', '')
        preview_type = os.getenv('PREVIEW_TYPE', '')
        preview_command = os.getenv('PREVIEW_COMMAND', '@BINARY@ @INPUT@ @OUTPUT@')

        # add any additional arguments to parser
        self.parser.add_argument('--image-binary', nargs='?', dest='image_binary', default=image_binary,
                                 help='Image Binary used to for image thumbnail/preview (default=%s)' % image_binary)
        self.parser.add_argument('--image-type', nargs='?', dest='image_type', default=image_type,
                                 help='Image type of thumbnail/preview (default=%s)' % image_type)
        self.parser.add_argument('--image-thumbnail-command', nargs='?', dest='image_thumbnail_command',
                                 default=image_thumbnail_command,
                                 help='Image command line for thumbnail (default=%s)' % image_thumbnail_command)
        self.parser.add_argument('--image-preview-command', nargs='?', dest='image_preview_command',
                                 default=image_preview_command,
                                 help='Image command line for preview (default=%s)' % image_preview_command)
        self.parser.add_argument('--preview-binary', nargs='?', dest='preview_binary', default=preview_binary,
                                 help='Binary used to generate preview (default=%s)' % preview_binary)
        self.parser.add_argument('--preview-type', nargs='?', dest='preview_type', default=preview_type,
                                 help='Preview type (default=%s)' % preview_type)
        self.parser.add_argument('--preview-command', nargs='?', dest='preview_command', default=preview_command,
                                 help='Command line for preview (default=%s)' % preview_command)

        # parse command line and load default logging configuration
        self.setup()

        # setup logging for the exctractor
        logging.getLogger('pyclowder').setLevel(logging.DEBUG)
        logging.getLogger('__main__').setLevel(logging.DEBUG)

    def process_message(self, connector, host, secret_key, resource, parameters):
        # Process the file and upload the results

        inputfile = resource["local_paths"][0]
        file_id = resource['id']

        pdffile = re.sub(r"\..*$", ".pdf", inputfile)
        pngfile = re.sub(r"\..*$", ".png", inputfile)

        # create extractor specifc preview
        self.execute_command(connector, host, secret_key, inputfile, pdffile, file_id, resource, False,
                             self.args.preview_binary, self.args.preview_command, self.args.preview_type)

        # create thumbnail image
        self.execute_command(connector, host, secret_key, inputfile, pngfile, file_id, resource, False,
                             self.args.image_binary, self.args.image_thumbnail_command, self.args.image_type)

        # create preview image
        self.execute_command(connector, host, secret_key, inputfile, pngfile, file_id, resource, False,
                             self.args.image_binary, self.args.image_preview_command, self.args.image_type)

        try:
            os.remove(pdffile)
            os.remove(pngfile)
        except OSError:
            pass

    @staticmethod
    def execute_command(connector, host, key, inputfile, fileid, outputfile, resource, preview, binary, commandline, ext):
        logger = logging.getLogger(__name__)

        if binary is None or binary == '' or commandline is None or commandline == '' or ext is None or ext == '':
            return

        try:
            # replace some special tokens
            commandline = commandline.replace('@BINARY@', binary)
            commandline = commandline.replace('@INPUT@', inputfile)
            commandline = commandline.replace('@OUTPUT@', outputfile)

            # split command line
            p = re.compile(r'''((?:[^ "']|"[^"]*"|'[^']*')+)''')
            commandline = p.split(commandline)[1::2]

            # execute command
            x = subprocess.check_output(commandline, stderr=subprocess.STDOUT)
            if x:
                logger.debug(binary + " : " + x)

            if os.path.getsize(outputfile) != 0:
                # upload result
                if preview:
                    pyclowder.files.upload_preview(connector, host, key, fileid, outputfile, None)
                    connector.status_update(pyclowder.utils.StatusMessage.processing, resource,
                                            "Uploaded preview of type %s" % ext)
                else:
                    pyclowder.files.upload_thumbnail(connector, host, key, fileid, outputfile)
                    connector.status_update(pyclowder.utils.StatusMessage.processing, resource,
                                            "Uploaded thumbnail of type %s" % ext)
            else:
                logger.warning("Extraction resulted in 0 byte file, nothing uploaded.")

        except subprocess.CalledProcessError as e:
            logger.error(binary + " : " + str(e.output))
            raise


if __name__ == "__main__":
    extractor = OfficePreviewExtractor()
    extractor.start()
