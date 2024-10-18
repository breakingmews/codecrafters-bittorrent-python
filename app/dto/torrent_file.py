import hashlib
import math
from dataclasses import dataclass
from typing import List

import bencodepy


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
    content: bytes
    pieces: List[Piece]

    def __init__(self, filepath: str):
        bc = bencodepy.Bencode()
        content = bc.read(filepath)
        print(f"Torrent filepath: {filepath}")
        print(f"Torrent file content: {content}")

        self.content = content
        self.pieces = self._parse_pieces()

    @property
    def tracker(self):
        return self.content[b"announce"].decode()

    @property
    def info(self):
        return self.content[b"info"]

    @property
    def length(self):
        return self.info[b"length"]

    @property
    def piece_length(self):
        return self.info[b"piece length"]

    @property
    def sha1_info_hash(self):
        return hashlib.sha1(bencodepy.encode(self.info)).digest()

    def __repr__(self):
        return (
            f"Tracker URL: {self.tracker}\n"
            + f"Length: {self.length}\n"
            + f"Info Hash: {self.sha1_info_hash.hex()}\n"
            + f"Piece Length: {self.piece_length}\n"
            + f"Piece Hashes:\n{"\n".join(piece.hash_ for piece in self.pieces)}"
        )

    def _parse_pieces(self) -> [str]:
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
