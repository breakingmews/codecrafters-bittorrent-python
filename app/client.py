import socket
import struct

import bencodepy
import requests

from app.const import PEER_ID
from app.dto import Handshake, TorrentFile


class Tracker:
    @staticmethod
    def get_peers(torrent_file: TorrentFile) -> [str]:
        sha1_info_hash = Tracker._url_encode_hash(torrent_file.sha1_info_hash.hex())

        url = f"{torrent_file.tracker}?info_hash={sha1_info_hash}"
        params = {
            "peer_id": PEER_ID,
            "port": 6881,
            "uploaded": 0,
            "downloaded": 0,
            "left": torrent_file.length,
            "compact": 1,
        }
        response = requests.get(url, params)
        decoded = bencodepy.decode(response.content)[b"peers"]
        peers = []
        start = 0
        while start < len(decoded):
            peer = decoded[start: start + 6]
            ip = ".".join(str(p) for p in list(peer[0:4]))
            port = str(struct.unpack("!H", bytes(peer[4:]))[0])
            peers.append(ip + ":" + port)
            start += 6
        return peers

    @staticmethod
    def _url_encode_hash(hash_):
        parts = [hash_[i: i + 2] for i in range(0, 40, 2)]
        hash_encoded = "".join(["%" + p for p in parts])
        return hash_encoded


class Peer:
    def __init__(self, peer: str):
        address = Peer._get_address(peer)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect(address)
        print(f"Connected to peer: {address}")

    @staticmethod
    def _get_address(peer: str):
        address = peer.split(":")[0], int(peer.split(":")[1])
        print(f"Peer address: {address}")
        return address

    def send(self, buffer: bytes):
        self.socket.sendall(buffer)
        return self.socket.recv(1024)

    def shake_hands(self, torrent_file: TorrentFile):
        handshake = Handshake(torrent_file.sha1_info_hash).encode()
        response = self.send(handshake)
        print(f"\nHandshake response: {response}")
        decoded = Handshake.decode(response)
        return decoded
