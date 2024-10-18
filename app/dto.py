import hashlib
import struct
from dataclasses import dataclass
from typing import List

import bencodepy

from app.const import PEER_ID


class TorrentFile:
    content: bytes
    tracker: str
    info: dict
    length: int
    sha1_info_hash: bytes
    piece_hashes: List[str] = []

    @staticmethod
    def read(filepath: str) -> "TorrentFile":
        bc = bencodepy.Bencode()
        content = bc.read(filepath)
        print(f"Torrent filepath: {filepath}")
        print(f"Torrent file content: {content}")

        file = TorrentFile()
        file.content = content
        return file

    def decode(self) -> "TorrentFile":
        self.tracker = self.content[b"announce"].decode()
        self.info = self.content[b"info"]
        self.length = self.info[b"length"]
        self.sha1_info_hash = hashlib.sha1(bencodepy.encode(self.info)).digest()
        self.piece_hashes = self._parse_hashes()
        return self

    def __repr__(self):
        return (
            f"Tracker URL: {self.tracker}\n"
            + f"Length: {self.length}\n"
            + f"Info Hash: {self.sha1_info_hash.hex()}\n"
            + f"Piece Length: {self.info[b"piece length"]}\n"
            + f"Piece Hashes:\n{"\n".join(self.piece_hashes)}"
        )

    def _parse_hashes(self) -> [str]:
        pieces: bytes = self.info[b"pieces"]
        hash_length = 20
        hashes = []
        start = 0
        while start < len(pieces) + hash_length:
            hash_ = pieces[start : start + hash_length].hex()
            if hash_:
                hashes.append(hash_)
            start += hash_length
        return hashes


@dataclass
class Handshake:
    sha1_info_hash: bytes
    peer_id: str = PEER_ID
    _length: int = 19
    _protocol: str = "BitTorrent protocol"
    _buffer: int = 0

    def __init__(self, sha1_info_hash=None, peer_id=None):
        self._length: int = 19
        self._protocol: str = "BitTorrent protocol"
        self._buffer: int = 0

        if sha1_info_hash:
            self.sha1_info_hash = sha1_info_hash
        if peer_id:
            self.peer_id = peer_id

    def encode(self):
        encoded = (
            struct.pack("!B", self._length)
            + self._protocol.encode()
            + struct.pack("!B", self._buffer) * 8
            + self.sha1_info_hash
            + self.peer_id.encode()
        )
        return encoded

    @staticmethod
    def decode(buffer: bytes):
        handshake = Handshake()
        handshake.sha1_info_hash = buffer[28:48].hex()
        handshake.peer_id = buffer[48:68].hex()
        return handshake


class PeerMessage:
    length: int  # 4 bytes
    id: str  # 1 byte
    payload: str  # variable


class BitField(PeerMessage):
    id = 5


class Interested(PeerMessage):
    id = 2
    # payload = ""


class Unchoke(PeerMessage):
    id = 1
    # payload = ""


# A piece is broken into blocks of 16 kiB (16 * 1024 bytes)


class Request(PeerMessage):
    id = 6
    index: int  # 4 bytes
    begin: int  # 4 bytes
    length: int  # 4 bytes


class Piece(PeerMessage):
    id = 7
    index: int  # 4 bytes
    begin: int  # 4 bytes
    block: str
