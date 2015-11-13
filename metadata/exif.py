#!/usr/bin/env python
import subprocess
import logging
import re
from config import *
import pyclowder.extractors as extractors

def main():
    global extractorName, messageType, rabbitmqExchange, rabbitmqURL    

    #set logging
    logging.basicConfig(format='%(levelname)-7s : %(name)s -  %(message)s', level=logging.WARN)
    logging.getLogger('pyclowder.extractors').setLevel(logging.INFO)

    #connect to rabbitmq
    extractors.connect_message_bus(extractorName=extractorName, messageType=messageType, processFileFunction=process_file, 
        rabbitmqExchange=rabbitmqExchange, rabbitmqURL=rabbitmqURL)

# ----------------------------------------------------------------------
def parseExif(text):
    # adapted from https://github.com/dandean/imagemagick-identify-parser
    text = str(text)

    if (text.strip() == ''):
        return {}

    # Each new line should start with *at least* two spaces. This fixes 1st line.
    lines = ('  ' + text.strip()).split("\n")

    lastDepth=1
    lastKey=""
    data={"raw": text}

    # parse all lines
    for line in lines:
        # skip empty lines
        if (line.strip() == ''):
            continue

        line = line.replace("\\r", "").replace("\\n", "").replace("\r", "").replace("\n", "")

        # The line *must* contain a colon to be processed.
        try:
            index=line.index(':')
            if index > -1:
                next_char = line[index+1]
                # next_char is undefined when ':' is last char on the line
                if next_char and re.match("/\w/", next_char):
                    # start counting from the first ':'
                    for j in range(index+1, line.length):
                        if line[j] == ':':
                            index = j
                            break

            depth=len(re.match(" +", line).group(0)) / 2
            key = line[0:index].strip()
            value = line[index+1:].strip() or {}
            #print("%d %d" % (index, depth))

            if depth==1 and re.match("/^Geometry$/i", key) and re.match("/^\d+x\d+\+\d+\+\d+$/", value):
                # Extract width and height from geometry property if present and value
                # is in format "INTxINT+INT+INT"
                parts = value.split('x')
                data["width"] = parts[0]
                data["height"] = parts[1]

            if depth==lastDepth:
                # Add the key/value pair to the last object in the stack
                data[key] = value

                # Note this key as the last key, which will become the parent key if the next object is a child.
                lastKey = key

            elif depth==lastDepth+1:
                # Add the last key (which should be an empty object) to the end of
                # the object stack. This allows us to match stack depth to
                # indentation depth.
                #stack.push(stack[stack.length-1][lastKey])
                data[key] = value

                lastDepth+=1
                lastKey = key

            elif depth < lastDepth:
                # Remove items from the end of the stack so that we add this new
                # key/value pair to the correct parent object.
                #stack = stack.slice(0, depth);
                data[key] = value;

                lastDepth = depth;
                lastKey = key;

        except Exception as e:
            print(e)
            print("Skipping : " + line)

    return data

# Process the file and upload the results
def process_file(parameters):
    global imageBinary
    print(parameters)
    input_file = parameters['inputfile']
    clowder_host = parameters['host']
    result = parseExif(subprocess.check_output([imageBinary, "-verbose", input_file], stderr=subprocess.STDOUT))

    metadata = {
        "@context": "http://www.w3.org/2003/12/exif/",
        "file_id": parameters["fileid"],
        "content": result,
        "agent": {
            "@type": "cat:extractor",
            "extractor_id": clowder_host+"/api/extractors/imageEXIF"
        }
    }

    extractors.upload_file_metadata_jsonld(mdata=metadata, parameters=parameters)

if __name__ == "__main__":
    main()





