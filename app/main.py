import hashlib
import json
import sys

import bencodepy

from app.client import do_handshake, get_peers
from app.codec import decode_file, decode_value
from app.dto import Handshake


def parse_hashes(info):
    pieces: bytes = info[b"pieces"]
    hash_length = 20
    hashes = []
    start = 0
    while start < len(pieces) + hash_length:
        hash_ = pieces[start : start + hash_length].hex()
        hashes.append(hash_)
        start += hash_length
    return "\n".join(hashes)


def main():
    command = sys.argv[1]
    arg = sys.argv[2]
    commands = ["decode", "info", "peers", "handshake"]

    if command not in commands:
        raise NotImplementedError(f"Unknown command {command}")

    if command == "decode":
        bencoded_value = arg
        decoded: str = decode_value(bencoded_value)
        print(json.dumps(decoded))
        return

    filepath = arg
    decoded: dict = decode_file(filepath)

    tracker = decoded[b"announce"].decode()
    info = decoded[b"info"]
    length = info[b"length"]
    sha1_info_hash: bytes = hashlib.sha1(bencodepy.encode(info)).digest()
    sha1_info_hash_hex = sha1_info_hash.hex()
    piece_hashes = parse_hashes(info)

    print(f"Tracker URL: {tracker}")
    print(f"Length: {length}")
    print(f"Info Hash: {sha1_info_hash_hex}")
    print(f"Piece Length: {info[b"piece length"]}")
    print(f"Piece Hashes:\n{piece_hashes}")

    if command == "info":
        return

    if command == "peers":
        peers = get_peers(tracker, sha1_info_hash_hex, length)
        print("\n".join(peers))

    if command == "handshake":
        peer = sys.argv[3]
        handshake: Handshake = do_handshake(peer, sha1_info_hash)
        print(f"Peer ID: {handshake.peer_id}")


if __name__ == "__main__":
    main()
