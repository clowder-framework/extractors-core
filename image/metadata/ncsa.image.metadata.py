#!/usr/bin/env python

import logging
import os
import re
import subprocess

from pyclowder.extractors import Extractor
import pyclowder.files
import pyclowder.utils

clowder_version = os.getenv('CLOWDER_VERSION')

class ImageMetadataExtractor(Extractor):
    """Count the number of characters, words and lines in a text file."""
    def __init__(self):
        Extractor.__init__(self)

        image_binary = os.getenv('IMAGE_BINARY', '/usr/bin/identify')

        # add any additional arguments to parser
        self.parser.add_argument('--image-binary', nargs='?', dest='image_binary', default=image_binary,
                                 help='Image Binary used to for image thumbnail/preview (default=%s)' % image_binary)

        # parse command line and load default logging configuration
        self.setup()

        # setup logging for the exctractor
        logging.getLogger('pyclowder').setLevel(logging.DEBUG)
        logging.getLogger('__main__').setLevel(logging.DEBUG)

    def process_message(self, connector, host, secret_key, resource, parameters):
        # Process the file and upload the results

        inputfile = resource["local_paths"][0]
        file_id = resource['id']

        result = self.parse_exif(subprocess.check_output(
            [self.args.image_binary, "-verbose", inputfile], stderr=subprocess.STDOUT).decode("utf-8"))

        if float(clowder_version) >= 2.0:
            context = {"@vocab": "http://www.w3.org/2003/12/exif/ns"}
            metadata = self.get_metadata(result, 'file', resource['id'], host, contexts=[context])
        else:
            metadata = {
                "@context": {
                    "@vocab": "http://www.w3.org/2003/12/exif/ns"
                },
                "file_id": file_id,
                "content": result,
                "agent": {
                    "@type": "cat:extractor",
                    "extractor_id": host + "/api/extractors/ncsa.image.metadata"
                }
            }
        pyclowder.files.upload_metadata(connector, host, secret_key, file_id, metadata)

    def fix_map(self, data):
        if isinstance(data, dict):
            result = {}
            for key, value in data.items():
                keys = re.split('\.|:', key)
                if len(keys) > 1:
                    last_key = keys[-1]
                    del keys[-1]
                    d = result
                    for x in keys:
                        if x not in d:
                            d[x] = {}
                        d = d[x]
                    if last_key in d:
                        print("ERROR: trying to assign a value again to same key " + last_key)
                    d[last_key] = self.fix_map(value)
                else:
                    result[key] = self.fix_map(value)
            return result
        else:
            return data

    def parse_exif(self, text):
        # Adapted from https://github.com/dandean/imagemagick-identify-parser
        text = str(text)
        if (text.strip() == ''):
            return {}

        # Each new line should start with *at least* two spaces. This fixes 1st line.
        lines = ('  ' + text.strip()).split("\n")

        # Our 'stack' will be a list of objects. The first object will be returned;
        # others are temporary objects to be nested in the main object.
        data = [{}]
        last_depth = 1
        last_key = ""

        for line in lines:
            if line.strip() == '':
                continue

            # Clear out encoded line breaks
            line = line.replace("\\r", "").replace("\\n", "").replace("\r", "").replace("\n", "")

            # The line *must* contain a colon to be processed.
            try:
                if (line.endswith(":")):
                    index = len(line) - 1
                else:
                    index = line.index(': ')
                if index > -1:
                    # next_char is undefined when ':' is last char on the line
                    next_char = line[index + 1] if len(line) > index + 1 else None
                    if next_char and re.match("/\w/", next_char):
                        # start counting from the first ':'
                        for j in range(index + 1, line.length):
                            if line[j] == ':':
                                index = j
                                break

                depth = int(len(re.match(" +", line).group(0)) / 2)
                key = line[0:index].strip()
                value = line[index + 1:].strip() if len(line) > index + 1 else {}

                # Attempt to interpret data types from strings
                if isinstance(value, str):
                    if re.match("^\-?\d+$", value):
                        value = int(value)
                    elif re.match("^\-?\d+?\.\d+$", value):
                        value = float(value)
                    elif re.match("^true$", value, flags=re.IGNORECASE):
                        value = True
                    elif re.match("^false$", value, flags=re.IGNORECASE):
                        value = False
                    elif re.match("^undefined$", value, flags=re.IGNORECASE):
                        continue

                if depth == 1 and re.match(
                        ".*Geometry$",
                        key,
                        flags=re.IGNORECASE) and re.match(
                        "^\d+x\d+\+\d+\+\d+$",
                        value):
                    # Extract width and height from "_Geometry" (e.g "Pagegeometry") property if present.
                    # value must be in format "INTxINT+INT+INT".
                    # Full raw entry will still be added to final result.
                    parts = value.split('+')[0].split('x')
                    data[0]["width"] = int(parts[0])
                    data[0]["height"] = int(parts[1])

                if (last_key == "Histogram" or last_key == "Colormap") and depth > 1:
                    # These two must be handled separately because ImageMagick does not align first digit of their lines
                    # so the depths get confused, e.g.
                    #        0: (  0,  0,  0) #000000 gray(0)
                    #       10: ( 10, 10, 10) #0A0A0A gray(10)
                    #      100: (100,100,100) #646464 gray(100)
                    # These are really all "depth+1" whatever depth the original Histogram/colormap was
                    if last_key in data[len(data) - 1]:
                        # First entry for this histogram/colormap, so make it a separate object in
                        # data list for now
                        sub_data = data[len(data) - 1].pop(last_key)
                        if last_key == "Histogram":
                            # Flip key/value because key is pixel count - not unique
                            sub_data[value] = int(key)
                        else:
                            sub_data[key] = value  # Colormap
                        sub_data["_EXIF_PARENT_KEY_NAME"] = last_key  # This lets us nest recursively if needd
                        data.append(sub_data)
                        last_depth += 1
                    else:
                        if last_key == "Histogram":
                            # Flip key/value because key is pixel count - not unique
                            data[len(data) - 1][value] = int(key)
                        else:
                            data[len(data) - 1][key] = value  # Colormap

                elif depth == last_depth:
                    # Add the key/value pair to the last object in the stack.
                    # Key will become the parent key if the next value is a child.
                    data[len(data) - 1][key] = value
                    last_key = key

                elif depth == last_depth + 1:
                    # Pop last key (which should be an empty object) from the main object and append
                    # to the end of the list, adding key/value pair to it. Depth is maintained.
                    sub_data = data[len(data) - 1].pop(last_key)
                    sub_data[key] = value
                    sub_data["_EXIF_PARENT_KEY_NAME"] = last_key  # This lets us nest recursively if needd
                    data.append(sub_data)
                    last_depth += 1
                    last_key = key

                elif depth < last_depth:
                    # Remove object(s) from end of the stack so that we add this new
                    # key/value pair to the correct parent object.
                    while last_depth != depth:
                        last_depth -= 1
                        sub_data = data.pop()
                        parent_key = sub_data.pop("_EXIF_PARENT_KEY_NAME")
                        data = data[:last_depth]
                        data[len(data) - 1][parent_key] = sub_data
                    data[len(data) - 1][key] = value
                    last_key = key

            except Exception as e:
                print(e)
                print("Skipping : " + line)

        # Add raw source onto the primary dictionary object and return it
        #data[0]["raw"] = text
        return self.fix_map(data[0])


if __name__ == "__main__":
    extractor = ImageMetadataExtractor()
    extractor.start()
