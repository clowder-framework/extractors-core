This repository will contain the core extractors that most people would like to install:

- image  : creates image previews, thumbnails and extracts metadata
- video  : creates image previews, thumbnails and video previews
- audio  : creates image previews, thumbnails and audio previews
- pdf    : creates image previews, thumbnails and pdf previews
- office : creates image previews, thumbnails and pdf previews

You can build the docker containers using the command: `./docker.sh`

To test these extractors use the docker-compose file in clowder.

There is only a master branch, any changes made should be made to master. When making
changes to the code, bump the version in the extractor_info.json as well as update the
CHANGELOG.md
