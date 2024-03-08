"""This version does not currently work. Just leaving it here until I can figure out why not."""

import os
import tempfile


def textpreview(input_file_path):
    """
    This function keeps the first 1000 lines of a text files and uploads them as a preview to the file.

    :param input_file_path: Full path to the input file
    :return: Result dictionary containing the path on disk of the preview
    """
    numlines = 10

    with open(input_file_path, 'r') as file:
        lines = file.readlines(numlines)
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp:
            for line in lines:
                print("Line " + line)
                tmp.write(line)

        # (fd, tmp) = tempfile.mkstemp(suffix='.txt')
        # with open(tmp, 'w') as f:
        #     for line in lines:
        #         print("Line " + line)
        #         f.write(line)
        # os.close(fd)

    # return the path of preview on disk
    print("Preview path " + tmp.name)
    result = {
        'previews': [tmp.name]
    }

    # Return the result dictionary
    return result
