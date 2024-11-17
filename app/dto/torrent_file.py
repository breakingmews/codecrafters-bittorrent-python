import hashlib
import logging
import math
from dataclasses import dataclass
from typing import Any, List

import bencodepy

from app.dto.magnet import Data, Magnet

_log = logging.getLogger(__name__)


@dataclass
class Block:
    ix: int
    offset: int
    size: int


class Piece:
    _block_size: int = 16384  # 16 * 1024 bytes

    ix: int
    hash_: str
    size: int
    blocks: List[Block] = []

    def __init__(self, ix: int, hash_: str, size):
        self.ix = ix
        self.hash_ = hash_
        self.size = size
        self.blocks = self._calculate_blocks()

    def _calculate_blocks(self):
        blocks_count = self.size / self._block_size

        if blocks_count.is_integer():
            block_sizes = int(blocks_count) * [self._block_size]
        else:
            blocks_count = int(math.ceil(blocks_count))
            last_block_size = self.size - (blocks_count - 1) * self._block_size
            block_sizes = (blocks_count - 1) * [self._block_size] + [last_block_size]

        blocks = []
        for i in range(len(block_sizes)):
            block = Block(i, i * self._block_size, block_sizes[i])
            blocks.append(block)

        return blocks


class TorrentFile:
    content: dict[bytes, Any]
    pieces: List[Piece]

    @staticmethod
    def from_file(filepath: str) -> "TorrentFile":
        bc = bencodepy.Bencode()
        content = bc.read(filepath)
        _log.debug(f"Torrent filepath: {filepath}")
        _log.debug(f"Torrent file content: {content}")

        file = TorrentFile()
        file.content = content
        file.pieces = file._parse_pieces()
        return file

    @staticmethod
    def from_metadata(magnet: Magnet, metadata: Data) -> "TorrentFile":
        _log.debug(f"Magnet: {magnet}")
        _log.debug(f"Metadata: {metadata}")

        content = {
            b"announce": bytes(magnet.tracker, encoding="utf-8"),
            b"info": {
                b"sha1_info_hash": magnet.sha1_info_hash,
                # TODO workaround for hash from magnet link instead of calculated from actual info
                b"length": metadata.payload[b"length"],
                b"piece length": metadata.payload[b"piece length"],
                b"pieces": metadata.payload[b"pieces"],
            },
        }

        file = TorrentFile()
        file.content = content
        file.pieces = file._parse_pieces()
        return file

    @property
    def tracker(self):
        return self.content[b"announce"].decode()

    @property
    def info(self) -> dict:
        return self.content[b"info"]

    @property
    def length(self):
        return self.info[b"length"]

    @property
    def piece_length(self):
        return self.info[b"piece length"]

    @property
    def sha1_info_hash(self):
        if b"sha1_info_hash" in self.info.keys():
            return self.info[b"sha1_info_hash"]
        return hashlib.sha1(bencodepy.encode(self.info)).digest()  # nosec

    def __repr__(self):
        return (
            f"Tracker URL: {self.tracker}\n"
            + f"Length: {self.length}\n"
            + f"Info Hash: {self.sha1_info_hash.hex()}\n"
            + f"Piece Length: {self.piece_length}\n"
            + f"Piece Hashes:\n{"\n".join(piece.hash_ for piece in self.pieces)}"
        )

    def _parse_pieces(self) -> List[Piece]:
        pieces_bytes: bytes = self.info[b"pieces"]
        hash_length = 20
        hashes = []
        start = 0
        while start < len(pieces_bytes) + hash_length:
            hash_ = pieces_bytes[start : start + hash_length].hex()
            if hash_:
                hashes.append(hash_)
            start += hash_length

        pieces = []
        piece_sizes = TorrentFile._calculate_piece_sizes(
            self.length, self.piece_length, hashes
        )
        for i in range(len(hashes)):
            piece = Piece(i, hashes[i], piece_sizes[i])
            pieces.append(piece)

        return pieces

    @staticmethod
    def _calculate_piece_sizes(length, piece_length, piece_hashes):
        pieces_count = len(piece_hashes)

        if length % piece_length == 0:
            return piece_length * [pieces_count]

        last_piece_size = length - (pieces_count - 1) * piece_length
        return (pieces_count - 1) * [piece_length] + [last_piece_size]
