import logging
import struct
from dataclasses import dataclass
from typing import Any

import bitstruct

from app.core.const import PEER_ID

_log = logging.getLogger(__name__)


@dataclass
class Handshake:
    buffer: tuple
    sha1_info_hash: bytes
    peer_id: str = PEER_ID
    _length: int = 19
    _protocol: str = "BitTorrent protocol"

    def __init__(self, sha1_info_hash=None, peer_id=None, supports_extensions=False):
        self._length: int = 19
        self._protocol: str = "BitTorrent protocol"
        self.buffer: tuple = (
            (0, 0, 0, 0, 0, 16, 0, 0)
            if supports_extensions
            else (0, 0, 0, 0, 0, 0, 0, 0)
        )

        if sha1_info_hash:
            self.sha1_info_hash = sha1_info_hash
        if peer_id:
            self.peer_id = peer_id

    def encode(self):
        encoded = (
            struct.pack("!B", self._length)
            + self._protocol.encode()
            + struct.pack("!BBBBBBBB", *self.buffer)
            + self.sha1_info_hash
            + self.peer_id.encode()
        )
        return encoded

    @staticmethod
    def decode(buffer: bytes):
        handshake = Handshake()
        handshake.sha1_info_hash = buffer[28:48].hex()
        handshake.peer_id = buffer[48:68].hex()
        handshake.buffer = struct.unpack("!BBBBBBBB", buffer[20:28])
        return handshake

    @property
    def supports_extensions(self):
        return self.buffer[5] == 16


# TODO make abstract class
@dataclass
class PeerMessage:
    id_: int  # 1 byte
    payload: Any  # variable
    length: int = 0  # 4 bytes

    def encode(self):
        encoded = struct.pack("!IB", self.length, self.id_)
        return encoded

    @staticmethod
    def decode(buffer: bytes):
        length, id_ = struct.unpack("!IB", buffer[:5])
        payload = buffer[5:]
        decoded = PeerMessage(id_=id_, length=length, payload=payload)
        _log.debug(f"Decoded PeerMessage: {decoded}")
        return decoded

    @staticmethod
    def is_keep_alive(buffer) -> bool:
        return len(buffer) == 0 or buffer == b"\x00\x00\x00\x00"

    @staticmethod
    def is_bitfield(buffer) -> bool:
        return buffer and len(buffer) > 4 and (buffer[4] == BitField.id_)


@dataclass
class BitField(PeerMessage):
    id_ = 5

    @staticmethod
    def decode(buffer: bytes):
        _log.debug(f"Decoding BitField: {buffer}")
        length, id_ = struct.unpack("!IB", buffer[:5])
        payload = bitstruct.unpack("u1" * 8 * (length - 1), buffer[5 : 5 + length])
        bitfield = BitField(id_=id_, length=length, payload=payload)
        _log.debug(f"Bitfield decoded: {bitfield}")
        return bitfield


@dataclass
class Interested(PeerMessage):
    id_ = 2
    length = 1

    # payload = ""
    def __init__(self):
        super()


@dataclass
class Unchoke(PeerMessage):
    id_: int = 1
    payload: str = ""

    @staticmethod
    def decode(buffer: bytes):
        length, id_ = struct.unpack("!IB", buffer)
        decoded = Unchoke(id_=id_, length=length)
        _log.debug(f"Decoded Unchoke: {decoded}")
        return decoded


@dataclass
class Request(PeerMessage):
    id_ = 6  # 1 byte

    length = 1 + 4 + 4 + 4
    piece_index: int = 0  # 4 bytes
    begin: int = 0  # 4 bytes

    # A piece is broken into blocks of 16 kiB (16 * 1024 bytes)
    block_size: int = 16 * 1024  # 4 bytes

    def __init__(self, piece_index: int, begin: int, block_size: int):
        self.piece_index = piece_index
        self.begin = begin
        self.block_size = block_size

    def encode(self):
        encoded = struct.pack(
            "!IBIII",
            self.length,
            self.id_,
            self.piece_index,
            self.begin,
            self.block_size,
        )
        return encoded

    def __repr__(self):
        return f"length={self.length}, id_={self.id_}, piece_index={self.piece_index}, begin={self.begin}, block_size={self.block_size}"


class Piece(PeerMessage):
    id_ = 7
    index: int  # 4 bytes
    begin: int  # 4 bytes
    block: bytes

    def __init__(self, length, id_, index, begin, payload):
        self.length = length
        self.id_ = id_
        self.index = index
        self.begin = begin
        self.payload = payload

    def __repr__(self):
        return f"length={self.length}, id_={self.id_}, index={self.index}, begin={self.begin}"

    @staticmethod
    def decode(buffer: bytes):
        length, id_, index, begin = struct.unpack("!IBII", buffer[:13])
        payload = buffer[13:]
        piece = Piece(length=length, id_=id_, index=index, begin=begin, payload=payload)
        _log.debug(f"Decoded Piece: {piece}")
        return piece
