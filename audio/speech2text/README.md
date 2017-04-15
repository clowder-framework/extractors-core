# Speech2Text Extractor

## Requirements

Speech2text requires uses CMU Sphinx to extract text from audio files and requires java, maven, and ffmpeg.



## Starting the extractor

To start the extractor you will need to compile and run it, this can be done in the following ways:

```
mvn exec:java
```

or 

```
mvn package
java -jar target/speech2text-1.0.0-SNAPSHOT-jar-with-dependencies.jar
```

## Docker Setup

### Clone repo
```
git clone ssh://git@opensource.ncsa.illinois.edu:7999/cats/extractors-core.git
```
There are a bunch of extractors in this repo.  To get to the Speech2text extractor:

```
cd extractors-core/audio/speech2text
```

### Build the jar outside of docker
```
mvn package
```

### Start dependency containers: mongo, clowder, rabbitmq

```
docker-compose up
```

### Build extractor container
As of 6/21/2016, the ffmpeg install takes a long time.

```
docker build -t speech2text .
```

### Start extractor container
```
docker run --rm -i -t --link speech2text_rabbitmq_1:rabbitmq speech2text
```

If the extractor starts correctly you will see something like:

```
15:26:10,880  INFO ExtractText:126 - [*] Waiting for messages. To exit press CTRL+C
```

## Clowder

### Get Clowder IP:Port, Login

1. Get IP/Port
    * Option 1: Kitematic: Select the running Clowder container in Kitematic, in the home tab on the right the ip:port is displayed under 'ACCESS URL'
2. Go to that IP in your browser
3. Select 'Sign Up' in the upper right corner, enter email address, push 'Create Account'.  It will not send you an email despite the message.
4. Look in clowder container console for an href link under 'Please follow this'.  It will look like 'http://192.168.99.100:9000/signup/f031f3d6-f810-4081-9c5d-eab2559d1dbf'.  Paste the link in your browser, then signup.

### Run Extractor

1. Create a dataset
2. Upload a file to dataset
3. Wait a bit.  You can watch the extractor output in the extractor console - it's finished when you see something like '16:19:52,962 DEBUG ExtractText:181 - [57696909e4b088193c1f53ad] : Done'

















