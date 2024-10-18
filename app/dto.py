import struct
from dataclasses import dataclass

from app.const import PEER_ID


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
