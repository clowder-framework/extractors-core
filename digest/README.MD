# Clowder File Digest Extractor

This will generate hash digests (MD5, SHA-512, etc.) for files uploaded to Clowder. 

# Installation and Running

To install and run the python extractor do the following:

1. Install pyclowder2
   `pip install git+https://opensource.ncsa.illinois.edu/stash/scm/cats/pyclowder2.git`
2. Start extractor `python ncsa.file.digest.py`

# Building Docker Image
`docker build -t clowder/extractors-digest:latest .`
