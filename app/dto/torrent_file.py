import hashlib
from typing import List

import bencodepy


class TorrentFile:
    content: bytes
    tracker: str
    info: dict
    length: int
    piece_length: int
    sha1_info_hash: bytes
    piece_hashes: List[str] = []
    _piece_sizes: List[int] = []

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
        self.piece_length = self.info[b"piece length"]
        self._piece_sizes = self._calculate_piece_sizes()
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

    def _calculate_piece_sizes(self):
        pieces_count = len(self.piece_hashes)

        if self.length % self.piece_length == 0:
            self._piece_sizes = self.piece_length * [pieces_count]
            return

        last_piece_size = self.length - (pieces_count - 1) * self.piece_length
        self._piece_sizes = (pieces_count - 1) * [self.piece_length] + [last_piece_size]
