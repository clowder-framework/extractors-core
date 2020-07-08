# Change Log
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).


# 2020-07-08

## 2.1.0 - file/digest

### Changed

- redid building of container to use pyenv and install pyclowder

# 2020-07-07

## 1.0.1 - audio/speech2text

### Fixed

- Updated dependencies for audio

## 2.0.1 - pdf/preview 

### Fixed

- Fix pdf preview no authroization by updating policy.xml.

# 2018-05-24

### Changed
- All core extractors now use PyClowder2
- Uses larger chunk size

### Fixed
- Fixed bug in release shell script code.
- Fixed maintainer name spelling
- Use 10KB blocks when computing digest for faster computation.
