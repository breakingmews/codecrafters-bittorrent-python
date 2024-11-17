import struct
from typing import List

import bencodepy
import requests

from app.core.const import PEER_ID
from app.dto.magnet import Magnet
from app.dto.torrent_file import TorrentFile


class Tracker:
    @staticmethod
    def get_peers(torrent_file: TorrentFile) -> List[str]:
        tracker = torrent_file.tracker
        info_hash = torrent_file.sha1_info_hash.hex()
        left = torrent_file.length
        return Tracker._get_peers(tracker, info_hash, left)

    @staticmethod
    def _get_peers(tracker: str, info_hash: str, left: int = 1024):
        sha1_info_hash = Tracker._url_encode_hash(info_hash)
        url = f"{tracker}?info_hash={sha1_info_hash}"
        params: dict = {
            "peer_id": PEER_ID,
            "port": 6881,
            "uploaded": 0,
            "downloaded": 0,
            "left": left,
            "compact": 1,
        }
        response = requests.get(url, params, timeout=5)
        decoded = bencodepy.decode(response.content)[b"peers"]
        peers = []
        start = 0
        while start < len(decoded):
            peer = decoded[start : start + 6]
            ip = ".".join(str(p) for p in list(peer[0:4]))
            port = str(struct.unpack("!H", bytes(peer[4:]))[0])
            peers.append(ip + ":" + port)
            start += 6
        return peers

    @staticmethod
    def get_peers_from_magnet(magnet: Magnet):
        return Tracker._get_peers(magnet.tracker, magnet.info_hash)

    @staticmethod
    def _url_encode_hash(hash_):
        parts = [hash_[i : i + 2] for i in range(0, 40, 2)]
        hash_encoded = "".join(["%" + p for p in parts])
        return hash_encoded
