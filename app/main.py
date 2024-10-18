import hashlib
import json
import struct
import sys

import bencodepy
import requests


def decode_value(bencoded_value):
    bc = bencodepy.Bencode(encoding="utf-8")
    return bc.decode(bencoded_value)


def decode_file(filepath: str):
    bc = bencodepy.Bencode()
    content = bc.read(filepath)
    print(content)
    return content


def calculate_hash(info):
    encoded = bencodepy.encode(info)
    return hashlib.sha1(encoded).hexdigest()


def parse_hashes(info):
    pieces: bytes = info[b"pieces"]
    hash_length = 20
    hashes = []
    start = 0
    while start < len(pieces) + hash_length:
        hash_ = pieces[start: start + hash_length].hex()
        hashes.append(hash_)
        start += hash_length
    return "\n".join(hashes)


def encode_hash(hash_):
    parts = [hash_[i:i + 2] for i in range(0, 40, 2)]
    hash_encoded = "".join(["%" + p for p in parts])
    return hash_encoded


def get_peers(tracker, info, length):
    encoded_hash = encode_hash(calculate_hash(info))
    url = f"{tracker}?info_hash={encoded_hash}"
    params = {
        "peer_id": "00112233445566777777",
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
        peer = decoded[start: start + 6]
        ip = ".".join(str(p) for p in list(peer[0:4]))
        port = str(struct.unpack("!H", bytes(peer[4:]))[0])
        peers.append(ip + ":" + port)
        start += 6
    return peers


def main():
    command = sys.argv[1]
    arg = sys.argv[2]
    commands = ["decode", "info", "peers"]

    if command not in commands:
        raise NotImplementedError(f"Unknown command {command}")

    if command == "decode":
        bencoded_value = arg
        decoded: str = decode_value(bencoded_value)
        print(json.dumps(decoded))
        return

    filepath = arg
    decoded: dict = decode_file(filepath)
    print(decoded)
    tracker = decoded[b"announce"].decode()
    info = decoded[b"info"]
    length = info[b"length"]
    hash_ = hashlib.sha1(bencodepy.encode(info)).digest().hex()
    piece_hashes = parse_hashes(info)

    print(f"Tracker URL: {tracker}")
    print(f"Length: {length}")
    print(f"Info Hash: {hash_}")
    print(f"Piece Length: {info[b"piece length"]}")
    print(f"Piece Hashes:\n{piece_hashes}")

    if command == "info":
        return

    if command == "peers":
        peers = get_peers(tracker, info, length)
        print("\n".join(peers))


if __name__ == "__main__":
    main()
