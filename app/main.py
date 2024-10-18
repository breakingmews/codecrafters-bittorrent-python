import json
import sys
import bencodepy


def decode_value(bencoded_value):
    bc = bencodepy.Bencode(encoding="utf-8")
    return bc.decode(bencoded_value)


def decode_file(filepath: str):
    bc = bencodepy.Bencode()
    content = bc.read(filepath)
    # print(content)
    return content


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
        # print(read_file(filepath))
        decoded: dict = decode_file(filepath)
        print(f"Tracker URL: {decoded[b"announce"].decode()}")
        print(f"Length: {decoded[b"info"][b"length"]}")




if __name__ == "__main__":
    main()
