This repository will contain the core extractors that most people
would like to install:

- image : creates image previews, thumbnails and extracts metadata
- video : creates image previews, thumbnails and video previews
- audio : creates image previews, thumbnails and audio previews
- pdf   : creates image previews, thumbnails and pdf previews

You can build the docker containers using the command:
```
PUSH="nope" ./docker.sh 
```

Then to run clowder with all containers you can run:
```
docker-compose up
```
