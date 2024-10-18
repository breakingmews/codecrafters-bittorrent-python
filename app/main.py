import json
import sys
import bencodepy
import hashlib
import itertools

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
    print(len(pieces))
    hash_length = 20
    hashes = []
    start = 0
    while start < len(pieces) + hash_length:
        hash_ = pieces[start:start+hash_length].hex()
        hashes.append(hash_)
        print(start)
        print(hash_)
        start += hash_length

    return "\n".join(hashes)


def main():
    command = sys.argv[1]
    commands = ["decode", "info"]
    if not(command in commands):
        raise NotImplementedError(f"Unknown command {command}")

    if command == "decode":
        bencoded_value = sys.argv[2]
        decoded: str = decode_value(bencoded_value)
        print(json.dumps(decoded))
    elif command == "info":
        filepath =  sys.argv[2]
        decoded: dict = decode_file(filepath)
        print(decoded)
        info = decoded[b"info"]
        hash_ = calculate_hash(info)
        piece_hashes = parse_hashes(info)
        print(f"Tracker URL: {decoded[b"announce"].decode()}")
        print(f"Length: {info[b"length"]}")
        print(f"Info Hash: {hash_}")
        print(f"Piece Length: {info[b"piece length"]}")
        print(f"Piece Hashes:\n{piece_hashes}")





if __name__ == "__main__":
    main()
