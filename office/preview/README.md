# Installation

This extractor uses the following python packages: requests, pika and pyClowder and it needs libreoffice and imagemagick. You can install pika and requests using pip. For pyClowder you can clone the repository and create a symlink. The following block of command should take care of all of this:

```
pip install pika requests
(cd ../.. && git clone https://opensource.ncsa.illinois.edu/bitbucket/scm/cats/pyclowder.git)
ln -s ../../pyClowder/pyclowder pyclowder
```

To start the extractor execute `ncsa.office.preview.py`. To enable automatic starting of the extractor copy and modify the paths in clowder-office-preview.conf.

# Configuration

All the configuration of the script is done in config.py:

- rabbitmqURL : The rabbitmq server, see also [https://www.rabbitmq.com/uri-spec.html]. The default is to connect to a rabbitmq server on the local machine.
