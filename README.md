# Clowder Core Extractors

This repository contain the core extractors that most people would like to install:

- image  : creates image previews, thumbnails and extracts metadata
- video  : creates image previews, thumbnails and video previews
- audio  : creates image previews, thumbnails and audio previews
- pdf    : creates image previews, thumbnails and pdf previews
- office : creates image previews, thumbnails and pdf previews

To test these extractors use the docker-compose file in clowder.

All code pull requests in this repo should be created against the `main` branch, and it's the default one. When making
changes to the code, bump the version in the `extractor_info.json` as well as update the
CHANGELOG.md

## Support for Clowder V2

When running extractors against a Clowder V2 instance, pass the environment variable `CLOWDER_VERSION=2` to the running
Python program or Docker container.

### Docker Build and Run Instructions for Clowder V2

CD into the directory containing the specific extractor:

```shell
docker build -t <extractor-docker-image-name> .
docker run --rm -e CLOWDER_VERSION=2 -e "RABBITMQ_URI=amqp://guest:guest@rabbitmq:5672/%2f" --network <clowder_nework_name> <extractor-docker-image-name>
```

E.g., For image preview extractor, the build and run commands could be:

```shell
docker build -t clowder/extractors-image-preview .
docker run --rm -e CLOWDER_VERSION=2 -e "RABBITMQ_URI=amqp://guest:guest@rabbitmq:5672/%2f" --network clowder2-dev_clowder2 clowder/extractors-image-preview
```
