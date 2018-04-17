This repository will contain the core extractors that most people would like to install:

- image  : creates image previews, thumbnails and extracts metadata
- video  : creates image previews, thumbnails and video previews
- audio  : creates image previews, thumbnails and audio previews
- pdf    : creates image previews, thumbnails and pdf previews
- office : creates image previews, thumbnails and pdf previews

You can build the docker containers using the command: `./docker.sh`

To test these extractors use teh docker-compose file in clowder.


RELEASE

To create a release of the core extractors do the following (in this case the release is 2.0.0):
- update the version number in all extractor_info.json files:
  `find . -name extractor_info.json -exec sed -i~ 's/"version":.*/"version": "2.0.0",/' {} \;`.
- update the version number in docker.sh
- commit changes to develop, and create pull request to master
- once pull request is merged
- push all images to docker hub: `PUSH="yes" ./docker.sh`
