#!/usr/bin/env python
import json
import logging
import os
import re
import subprocess
import tempfile

import pyclowder.files
import pyclowder.utils
from pyclowder.extractors import Extractor
from requests_toolbelt import MultipartEncoder


class BinaryPreviewExtractor(Extractor):
    """Generate image preview and thumbnail and upload to Clowder."""

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

        # setup logging for the extractor
        logging.getLogger('pyclowder').setLevel(logging.DEBUG)
        logging.getLogger('__main__').setLevel(logging.DEBUG)

    def process_message(self, connector, host, secret_key, resource, parameters):
        # Process the file and upload the results

        inputfile = resource["local_paths"][0]
        file_id = resource['id']

        # create thumbnail image
        if 'image_thumbnail' in parameters:
            args = parameters['image_thumbnail']
        else:
            args = self.args.image_thumbnail_command
        self.execute_command(connector, host, secret_key, inputfile, file_id, resource, False,
                             self.args.image_binary, args, self.args.image_type, self.extractor_info["name"])

        # create preview image
        if 'image_preview' in parameters:
            args = parameters['image_preview']
        else:
            args = self.args.image_preview_command
        self.execute_command(connector, host, secret_key, inputfile, file_id, resource, True,
                             self.args.image_binary, args, self.args.image_type, self.extractor_info["name"])

        # create extractor specific preview
        if 'preview' in parameters:
            args = parameters['preview']
        else:
            args = self.args.preview_command
        self.execute_command(connector, host, secret_key, inputfile, file_id, resource, True,
                             self.args.preview_binary, args, self.args.preview_type, self.extractor_info["name"])

    @staticmethod
    def execute_command(connector, host, key, inputfile, fileid, resource, preview, binary, commandline, ext,
                        extractor_name):
        logger = logging.getLogger(__name__)
        clowder_version = int(os.getenv('CLOWDER_VERSION', '1'))

        if binary is None or binary == '' or commandline is None or commandline == '' or ext is None or ext == '':
            return

        (fd, tmpfile) = tempfile.mkstemp(suffix='.' + ext)
        try:
            # close tempfile
            os.close(fd)

            # replace some special tokens
            commandline = commandline.replace('@BINARY@', binary)
            commandline = commandline.replace('@INPUT@', inputfile)
            commandline = commandline.replace('@OUTPUT@', tmpfile)

            # split command line
            p = re.compile(r'''((?:[^ "']|"[^"]*"|'[^']*')+)''')
            commandline = p.split(commandline)[1::2]

            # execute command
            x = subprocess.check_output(commandline, stderr=subprocess.STDOUT)
            x = x.decode('utf-8')
            if x:
                logger.debug(binary + " : " + x)

            if os.path.getsize(tmpfile) != 0:
                # upload result
                if preview:
                    if clowder_version == 2:
                        logger.debug("tmpfile: %s" % tmpfile)
                        preview_mimetype = "image/" + ext
                        logger.debug("mimetype: %s" % preview_mimetype)

                        # pyclowder.files.upload_preview(connector, host, key, fileid, tmpfile, None,
                        #                                preview_mimetype="image/png",
                        #                                visualization_name=extractor_name,
                        #                                visualization_component_id="basic-image-component")

                        visualization_config_id = None

                        # TODO: not sure why host ends with a slash?
                        if host.endswith("/"):
                            host = host[:-1]

                        if os.path.exists(tmpfile):

                            # upload visualization URL
                            visualization_config_url = '%s/api/v2/visualizations/config' % host

                            visualization_config_data = dict()

                            payload = json.dumps({
                                "resource": {
                                    "collection": "files",
                                    "resource_id": fileid
                                },
                                "client": host,
                                "parameters": visualization_config_data,
                                "visualization_mimetype": preview_mimetype,
                                "visualization_component_id": "basic-image-component"
                            })

                            headers = {
                                "X-API-KEY": key,
                                "Content-Type": "application/json"
                            }

                            response = connector.post(visualization_config_url, headers=headers, data=payload,
                                                      verify=connector.ssl_verify if connector else True)

                            if response.status_code == 200:
                                visualization_config_id = response.json()['id']
                                logger.debug("Uploaded visualization config ID = [%s]", visualization_config_id)
                            else:
                                logger.error("An error occurred when uploading visualization config to file: " + fileid)

                            if visualization_config_id is not None:
                                logger.debug("Posting visualization bytes")

                                # upload visualization URL
                                visualization_url = '%s/api/v2/visualizations?name=%s&description=%s&config=%s' % (
                                    host, extractor_name, "test overwrite pyclowder", visualization_config_id)

                                filename = os.path.basename(tmpfile)
                                if preview_mimetype is not None:
                                    multipart_encoder_object = MultipartEncoder(
                                        fields={'file': (filename, open(tmpfile, 'rb'), preview_mimetype)})
                                else:
                                    multipart_encoder_object = MultipartEncoder(
                                        fields={'file': (filename, open(tmpfile, 'rb'))})
                                headers = {'X-API-KEY': key,
                                           'Content-Type': multipart_encoder_object.content_type}
                                logger.debug("multipart_encoder_object", multipart_encoder_object.content_type)
                                logger.debug("visualization_url", visualization_url)
                                logger.debug("connector.ssl_verify", connector.ssl_verify)
                                response = connector.post(visualization_url, data=multipart_encoder_object,
                                                          headers=headers,
                                                          verify=connector.ssl_verify if connector else True,
                                                          timeout=30) # try add a timeout

                                if response.status_code == 200:
                                    preview_id = response.json()['id']
                                    logger.debug("Uploaded visualization data ID = [%s]", preview_id)
                                else:
                                    logger.error(
                                        "An error occurred when uploading the visualization data to file: " + fileid)
                        else:
                            logger.error("Visualization data file not found")

                        connector.message_process({"type": "file", "id": fileid}, "Uploading file preview.")
                        logger = logging.getLogger(__name__)

                    else:
                        pyclowder.files.upload_preview(connector, host, key, fileid, tmpfile, None)
                        connector.status_update(pyclowder.utils.StatusMessage.processing, resource,
                                                "Uploaded preview of type %s" % ext)
                else:
                    pyclowder.files.upload_thumbnail(connector, host, key, fileid, tmpfile)
                    connector.status_update(pyclowder.utils.StatusMessage.processing, resource,
                                            "Uploaded thumbnail of type %s" % ext)
            else:
                logger.warning("Extraction resulted in 0 byte file, nothing uploaded.")

        except subprocess.CalledProcessError as e:
            logger.error(binary + " : " + str(e.output))
            raise
        finally:
            try:
                os.remove(tmpfile)
            except OSError:
                pass


if __name__ == "__main__":
    extractor = BinaryPreviewExtractor()
    extractor.start()
