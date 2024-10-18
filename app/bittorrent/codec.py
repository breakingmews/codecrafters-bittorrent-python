import bencodepy


def decode_value(bencoded_value):
    bc = bencodepy.Bencode(encoding="utf-8")
    return bc.decode(bencoded_value)
