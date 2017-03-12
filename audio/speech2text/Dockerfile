FROM java:7
MAINTAINER Marcus Slavenas <slavenas@illinois.edu>

RUN apt-get update -y

### INSTALL FFMPEG ##############################################

RUN apt-get -y install autoconf automake build-essential libass-dev libfreetype6-dev libgpac-dev libsdl1.2-dev libtheora-dev libtool libva-dev libvdpau-dev libvorbis-dev libx11-dev libxext-dev libxfixes-dev pkg-config texi2html zlib1g-dev unzip wget

# Make ffmpeg_sources directory
RUN mkdir ~/ffmpeg_sources

# Install yasm
RUN apt-get -y install yasm

# Install libmp3lame MP3 audio encoder
RUN apt-get -y install libmp3lame-dev

# Install libopus Opus audio decoder
RUN apt-get -y install libopus-dev

# Install FFMPEG
RUN cd ~/ffmpeg_sources && wget http://ffmpeg.org/releases/ffmpeg-snapshot.tar.bz2 && tar xjvf ffmpeg-snapshot.tar.bz2 --owner root --group root --no-same-owner && cd ffmpeg && PKG_CONFIG_PATH="$HOME/ffmpeg_build/lib/pkgconfig" && export PKG_CONFIG_PATH && ./configure --prefix="$HOME/ffmpeg_build" --extra-cflags="-I$HOME/ffmpeg_build/include" --extra-ldflags="-L$HOME/ffmpeg_build/lib" --bindir="$HOME/bin" --extra-libs="-ldl" --enable-gpl --enable-libass --enable-libfreetype --enable-libmp3lame --enable-libopus --enable-libtheora --enable-libvorbis  --enable-nonfree && make && make install && make distclean && hash -r 

# Setup environment variables
RUN echo "MANPATH_MAP $HOME/bin $HOME/ffmpeg_build/share/man" >> ~/.manpath . ~/.profile

### DONE INSTALLING FFMPEG ########################################################
RUN apt-get -y install netcat

RUN mkdir /usr/src/speech2text
WORKDIR /usr/src/speech2text
COPY config.properties entrypoint.sh /usr/src/speech2text/
COPY src/ /usr/src/speech2text/src
COPY target/ /usr/src/speech2text/target

# Setup environment variables. These are passed into the container. You can change
# these to your setup. If RABBITMQ_URI is not set, it will try and use the rabbitmq
# server that is linked into the container.
ENV RABBITMQ_URI="" \
    RABBITMQ_EXCHANGE="clowder" \
    RABBITMQ_VHOST="%2F" \
    RABBITMQ_QUEUE="speech2text" \
    MAIN_SCRIPT="java -jar target/speech2text-1.0-SNAPSHOT-jar-with-dependencies.jar"
    ENV PATH /root/bin/:$PATH
    #MAIN_SCRIPT="java -Xms1024M -Xmx2048M -Xss1M -XX:+CMSClassUnloadingEnabled -XX:MaxPermSize=1024M -XX:ReservedCodeCacheSize=128M -jar target/speech2text-1.0-SNAPSHOT-jar-with-dependencies.jar"

ENTRYPOINT ["/usr/src/speech2text/entrypoint.sh"]
CMD ["extractor"]

