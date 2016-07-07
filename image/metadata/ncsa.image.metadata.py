#!/usr/bin/env python
import subprocess
import logging
import re
import json
from config import *
import pyclowder.extractors as extractors


def main():
    global extractorName, messageType, rabbitmqExchange, rabbitmqURL

    # set logging
    logging.basicConfig(format='%(levelname)-7s : %(name)s -  %(message)s', level=logging.WARN)
    logging.getLogger('pyclowder.extractors').setLevel(logging.INFO)

    # setup
    extractors.setup(extractorName=extractorName,
                       messageType=messageType,
                       rabbitmqURL=rabbitmqURL,
                       rabbitmqExchange=rabbitmqExchange)

    # register extractor info
    extractors.register_extractor(registrationEndpoints)

    # connect to rabbitmq
    extractors.connect_message_bus(extractorName=extractorName,
                                   messageType=messageType,
                                   processFileFunction=process_file,
                                   rabbitmqExchange=rabbitmqExchange,
                                   rabbitmqURL=rabbitmqURL)

# ----------------------------------------------------------------------
# this will split any key that has a : into smaller subsections


def fixMap(data):
    if isinstance(data, dict):
        result = {}
        for key, value in data.iteritems():
            keys = re.split('\.|:', key)
            if len(keys) > 1:
                lastKey = keys[-1]
                del keys[-1]
                d = result
                for x in keys:
                    if x not in d:
                        d[x] = {}
                    d = d[x]
                if lastKey in d:
                    print("ERROR: trying to assign a value again to same key " + lastKey)
                d[lastKey] = fixMap(value)
            else:
                result[key] = fixMap(value)
        return result
    else:
        return data


def parseExif(text):
    # Adapted from https://github.com/dandean/imagemagick-identify-parser
    text = str(text)
    if (text.strip() == ''):
        return {}

    # Each new line should start with *at least* two spaces. This fixes 1st line.
    lines = ('  ' + text.strip()).split("\n")

    # Our 'stack' will be a list of objects. The first object will be returned;
    # others are temporary objects to be nested in the main object.
    data = [{}]
    lastDepth = 1
    lastKey = ""

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

            if (lastKey == "Histogram" or lastKey == "Colormap") and depth > 1:
                # These two must be handled separately because ImageMagick does not align first digit of their lines
                # so the depths get confused, e.g.
                #        0: (  0,  0,  0) #000000 gray(0)
                #       10: ( 10, 10, 10) #0A0A0A gray(10)
                #      100: (100,100,100) #646464 gray(100)
                # These are really all "depth+1" whatever depth the original Histogram/colormap was
                if lastKey in data[len(data) - 1]:
                    # First entry for this histogram/colormap, so make it a separate object in
                    # data list for now
                    sub_data = data[len(data) - 1].pop(lastKey)
                    if lastKey == "Histogram":
                        # Flip key/value because key is pixel count - not unique
                        sub_data[value] = int(key)
                    else:
                        sub_data[key] = value  # Colormap
                    sub_data["_EXIF_PARENT_KEY_NAME"] = lastKey  # This lets us nest recursively if needd
                    data.append(sub_data)
                    lastDepth += 1
                else:
                    if lastKey == "Histogram":
                        # Flip key/value because key is pixel count - not unique
                        data[len(data) - 1][value] = int(key)
                    else:
                        data[len(data) - 1][key] = value  # Colormap

            elif depth == lastDepth:
                # Add the key/value pair to the last object in the stack.
                # Key will become the parent key if the next value is a child.
                data[len(data) - 1][key] = value
                lastKey = key

            elif depth == lastDepth + 1:
                # Pop last key (which should be an empty object) from the main object and append
                # to the end of the list, adding key/value pair to it. Depth is maintained.
                sub_data = data[len(data) - 1].pop(lastKey)
                sub_data[key] = value
                sub_data["_EXIF_PARENT_KEY_NAME"] = lastKey  # This lets us nest recursively if needd
                data.append(sub_data)
                lastDepth += 1
                lastKey = key

            elif depth < lastDepth:
                # Remove object(s) from end of the stack so that we add this new
                # key/value pair to the correct parent object.
                while lastDepth != depth:
                    lastDepth -= 1
                    sub_data = data.pop()
                    parent_key = sub_data.pop("_EXIF_PARENT_KEY_NAME")
                    data = data[:lastDepth]
                    data[len(data) - 1][parent_key] = sub_data
                data[len(data) - 1][key] = value
                lastKey = key

        except Exception as e:
            print(e)
            print("Skipping : " + line)

    # Add raw source onto the primary dictionary object and return it
    #data[0]["raw"] = text
    return fixMap(data[0])

# Process the file and upload the results


def process_file(parameters):
    global imageBinary

    input_file = parameters['inputfile']
    clowder_host = parameters['host']
    result = parseExif(subprocess.check_output(
        [imageBinary, "-verbose", input_file], stderr=subprocess.STDOUT))

    metadata = {
        "@context": {
            "@vocab": "http://www.w3.org/2003/12/exif/ns"
        },
        "file_id": parameters["fileid"],
        "content": result,
        "agent": {
            "@type": "cat:extractor",
            "extractor_id": clowder_host + "/api/extractors/ncsa.image.metadata"
        }
    }

    extractors.upload_file_metadata_jsonld(mdata=metadata, parameters=parameters)

if __name__ == "__main__":
    #global imageBinary
    # input_file="/Users/kooper/Downloads/1416AV_412r.ORF"
    #result=parseExif(subprocess.check_output([imageBinary, "-verbose", input_file], stderr=subprocess.STDOUT))
    #print(json.dumps(result, sort_keys=True,indent=4, separators=(',', ': ')))
    main()
