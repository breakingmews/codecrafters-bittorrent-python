[![Build and Test](https://github.com/breakingmews/codecrafters-bittorrent-python/actions/workflows/ci.yml/badge.svg)](https://github.com/breakingmews/codecrafters-bittorrent-python/actions/workflows/ci.yml)
[![Coverage](https://github.com/breakingmews/codecrafters-bittorrent-python/actions/workflows/badges.yml/badge.svg)]

This is a solution to the ["Build Your Own BitTorrent" Challenge](https://app.codecrafters.io/courses/bittorrent/overview).

A BitTorrent client that's capable of parsing a .torrent file and downloading a file from a peer. 

# Setup

Install dependencies, including development ones.

```shell
pipenv install --dev
```

Install pre-commit hooks
```sh
pipenv run pre-commit install --install-hooks
```

# Features

- Decode bencoded value
- Show torrent file info
- Discover peers
- Complete a handshake with peer
- Download a file piece using torrent file
- Download a file using torrent file
- Parse magnet link
- Request metadata extension
- Complete extension handshake with peer
- Download a file piece using magnet link
- Download a file using magnet link


# Usage

See help for usage examples

```shell
./bittorrent.sh -h
./bittorrent.sh info -h
```

E.g. show torrent file info
```shell
./bittorrent.sh info ./data/sample.torrent
```

```shell
Tracker URL: http://bittorrent-test-tracker.codecrafters.io/announce
Length: 92063
Info Hash: d69f91e6b2ae4c542468d1073a71d4ea13879a7f
Piece Length: 32768
Piece Hashes:
e876f67a2a8886e8f36b136726c30fa29703022d
6e2275e604a0766656736e81ff10b55204ad8d35
f00d937a0213df1982bc8d097227ad9e909acc17
```

# Tests

To run tests use the following command
```shell
pipenv run test
```