# Clowder File Digest Extractor

This will generate hash digests (MD5, SHA-512, etc.) for files uploaded to Clowder. 

# Installation and Running

To install and run the python extractor do the following:

1. Install pyclowder
   `pip install git+https://opensource.ncsa.illinois.edu/stash/scm/cats/pyclowder.git`
   or if you have pyclowder checked out as well (useful when developing)
   ln -s ../../pyClowder/pyclowder pyclowder
2. Modify config.py
3. Start extractor `python ncsa.file.digest.py`

# Building Docker Image
`docker build -t ncsa/clowder-extractors-digest:latest .`
