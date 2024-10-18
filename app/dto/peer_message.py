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


# TODO make abstract class
@dataclass
class PeerMessage:
    id_: str  # 1 byte
    payload: str  # variable
    length: int = 0  # 4 bytes

    def encode(self):
        encoded = struct.pack("!IB", self.length, self.id_)
        return encoded

    @staticmethod
    def decode(buffer: bytes):
        length, id_ = struct.unpack("!IB", buffer)
        decoded = PeerMessage(length, id_)
        return decoded


@dataclass
class BitField(PeerMessage):
    id_ = 5

    @staticmethod
    def decode(buffer: bytes):
        print(f"Decoding BitField: {buffer}")
        if len(buffer) == 0:
            print('Warning: empty bitfield')
            return
        
        length, id_, payload = struct.unpack("!IBH", buffer)
        bitfield = BitField(length, id_, payload)
        return bitfield


@dataclass
class Interested(PeerMessage):
    id_ = 2

    # payload = ""
    def __init__(self):
        super()


@dataclass
class Unchoke(PeerMessage):
    id_: int = 1
    payload: str = ""

    @staticmethod
    def decode(buffer: bytes):
        print(f"Decoding Unchoke: {buffer}")

        length = struct.unpack("!I", buffer)[0]
        decoded = Unchoke(length)
        return decoded


# A piece is broken into blocks of 16 kiB (16 * 1024 bytes)


@dataclass
class Request(PeerMessage):
    id_ = 6  # 1 byte

    index: int = 0  # 4 bytes
    begin: int = 0  # 4 bytes
    length_: int = 16 * 1024  # 4 bytes

    def __init__(self, index: int, begin: int, length_: int):
        self.index = index
        self.begin = begin
        self.length_ = length_

    def encode(self):
        encoded = struct.pack(
            "!IBIII", self.length, self.id_, self.index, self.begin, self.length_
        )
        return encoded


class Piece(PeerMessage):
    id_ = 7
    index: int  # 4 bytes
    begin: int  # 4 bytes
    block: str
