import socket
import struct

import bencodepy
import requests

from app.const import PEER_ID
from app.dto import Handshake


def url_encode_hash(hash_):
    parts = [hash_[i : i + 2] for i in range(0, 40, 2)]
    hash_encoded = "".join(["%" + p for p in parts])
    return hash_encoded


def get_peers(tracker, sha1_info_hash_hex, length):
    sha1_info_hash = url_encode_hash(sha1_info_hash_hex)

    url = f"{tracker}?info_hash={sha1_info_hash}"
    params = {
        "peer_id": PEER_ID,
        "port": 6881,
        "uploaded": 0,
        "downloaded": 0,
        "left": length,
        "compact": 1,
    }
    response = requests.get(url, params)
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


def get_address(peer: str):
    address = peer.split(":")[0], int(peer.split(":")[1])
    print(f"Peer address: {address}")
    return address


def do_handshake(peer: str, sha1_info_hash: bytes):
    handshake = Handshake(sha1_info_hash).encode()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(get_address(peer))
    s.sendall(handshake)
    response = s.recv(1024)
    print(f"\nHandshake response: {response}")
    decoded = Handshake.decode(response)
    return decoded
