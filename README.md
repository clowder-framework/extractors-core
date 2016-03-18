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

In each folder there is a *.service file. These files work with systemd installed on COREOS. You can copy them to the /etc/systemd/system folder and run the following commands to start, for example, the audio extractor:

```
sudo systemctl enable clowder-audio-preview.service
sudo systemctl start clowder-audio-preview.service
```

By adding these files the containers are persisten when the VM is restarted. If you want to download the latest version of a container you can simply run

```
sudo systemctl restart clowder-audio-preview.service
```
