# Clowder Core Extractors

This repository contain the core extractors that most people would like to install:

- image  : creates image previews, thumbnails and extracts metadata
- video  : creates image previews, thumbnails and video previews
- audio  : creates image previews, thumbnails and audio previews
- pdf    : creates image previews, thumbnails and pdf previews
- office : creates image previews, thumbnails and pdf previews

You can build the docker containers using the command: `./docker.sh`

To test these extractors use the docker-compose file in clowder.

All code pull requests in this repo should be created against the `main` branch, and it's the default one. When making
changes to the code, bump the version in the `extractor_info.json` as well as update the
CHANGELOG.md

## Support for Clowder V2

When running extractors against a Clowder V2 instance, pass the environment variable `CLOWDER_VERSION=2` to the running
Python program or Docker container. 
