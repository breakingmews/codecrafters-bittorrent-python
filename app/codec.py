import bencodepy


def decode_value(bencoded_value):
    bc = bencodepy.Bencode(encoding="utf-8")
    return bc.decode(bencoded_value)


def decode_file(filepath: str):
    bc = bencodepy.Bencode()
    content = bc.read(filepath)
    print(f"Torrent filepath: {filepath}")
    print(f"Torrent file content: {content}")
    return content
