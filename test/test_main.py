import unittest

from app.client import Peer, Tracker
from app.dto import TorrentFile
from app.main import (
    Handshake,
    decode_value,
)


class TestMain(unittest.TestCase):
    def test_decode_bencode_str_1(self):
        decoded = decode_value(b"5:hello")
        expected = "hello"
        self.assertEqual(expected, decoded)

    def test_decode_bencode_str_2(self):
        decoded = decode_value(b"10:hello12345")
        expected = "hello12345"
        self.assertEqual(expected, decoded)

    def test_decode_bencode_int(self):
        decoded = decode_value(b"i52e")
        expected = 52
        self.assertEqual(expected, decoded)

    def test_decode_bencode_list(self):
        decoded = decode_value(b"l5:helloi52ee")
        expected = ["hello", 52]
        self.assertEqual(expected, decoded)

    def test_decode_bencode_dict(self):
        decoded = decode_value(b"d3:foo3:bar5:helloi52ee")
        expected = {"foo": "bar", "hello": 52}
        self.assertEqual(expected, decoded)

    @unittest.skip("Test file generator")
    def test_write_torrent_file(self):
        content = b"d8:announce55:http://bittorrent-test-tracker.codecrafters.io/announce10:created by13:mktorrent 1.14:infod6:lengthi2994120e4:name12:codercat.gif12:piece lengthi262144e6:pieces240:<40\x9f\xae\xbf\x01\xe4\x9c\x0fc\xc9\x0b~\xdc\xc2%\x9bj\xd0\xb8Q\x9b.\xa9\xbb7?\xf5g\xf6DB\x81V\xc9\x8a\x1d\x00\xfc\x9d\xc8\x13fXu6\xf4\x8c \x98\xa1\xd7\x96\x92\xf2Y\x0f\xd9\xa6\x03<a\xe7\x17\xf8\xc0\xd1\xe5XPh\x0e\xb4Q\xe3T;b\x03oT\xe7F\xec6\x9fe\xf3-E\xf7{\x1f\x1c7b\x1f\xb9e\xc6VpKx\x10~\xd5S\xbd\x08\x13\xf9/\xefx\x02g\xc0{t1\xb8h17\xd2\x0f\xf5\x94\xb1\xf1\xbf?\x885\x16]h\xfb\x042\xbd\x8ew\x96\x08\xd2w\x82\xb7y\xc7s\x80b\xe9\xb5\n\xb5\xd6\xbc\x04\t\xa0\xf3\xa9P8Wf\x9dG\xfeu-Ew\xea\x00\xa8n\xe6\xab\xbc0\xcd\xdb\x80\n\x0bb\xd7\xa2\x96\x11\x11f\xd89x?R\xb7\x0f\x0c\x90-V\x19k\xd3\xee\x7f7\x9b]\xb5~;=\x8d\xb9\xe3M\xb6;K\xa1\xbe'\x93\t\x11\xaa7\xb3\xf9\x97\xddee"
        with open("test.torrent", "wb") as f:
            f.write(content)

    def test_decode_file(self):
        filepath = "test.torrent"
        file = TorrentFile.read(filepath)
        self.assertEqual(dict, type(file.content))

    def test_parse_hashes(self):
        # arrange
        filepath = "test.torrent"
        file = TorrentFile.read(filepath).decode()

        # act
        hashes = file._parse_hashes()

        # assert
        expected = [
            "3c34309faebf01e49c0f63c90b7edcc2259b6ad0",
            "b8519b2ea9bb373ff567f644428156c98a1d00fc",
            "9dc81366587536f48c2098a1d79692f2590fd9a6",
            "033c61e717f8c0d1e55850680eb451e3543b6203",
            "6f54e746ec369f65f32d45f77b1f1c37621fb965",
            "c656704b78107ed553bd0813f92fef780267c07b",
            "7431b8683137d20ff594b1f1bf3f8835165d68fb",
            "0432bd8e779608d27782b779c7738062e9b50ab5",
            "d6bc0409a0f3a9503857669d47fe752d4577ea00",
            "a86ee6abbc30cddb800a0b62d7a296111166d839",
            "783f52b70f0c902d56196bd3ee7f379b5db57e3b",
            "3d8db9e34db63b4ba1be27930911aa37b3f997dd",
        ]
        self.assertEqual(expected, hashes)

    def test_encode_hash(self):
        hash_ = "d69f91e6b2ae4c542468d1073a71d4ea13879a7f"
        expected = "%d6%9f%91%e6%b2%ae%4c%54%24%68%d1%07%3a%71%d4%ea%13%87%9a%7f"
        encoded = Tracker._url_encode_hash(hash_)
        self.assertEqual(expected, encoded)

    def test_encode_handshake(self):
        sha1_info_hash = b"c7e51462e85d8631c25f8c9b8c5479345a1de26b"
        encoded = Handshake(sha1_info_hash).encode()
        expected = b"\x13BitTorrent protocol\x00\x00\x00\x00\x00\x00\x00\x00c7e51462e85d8631c25f8c9b8c5479345a1de26b00112233445566777777"
        self.assertEqual(expected, encoded)

    def test_decode_handshake(self):
        buffer = b"\x13BitTorrent protocol\x00\x00\x00\x00\x00\x00\x00\x00\xc7\xe5\x14b\xe8]\x861\xc2_\x8c\x9b\x8cTy4Z\x1d\xe2k\xb8/Qc{\xf2\xd2\x1f\xd8,*\x82Z69\xb0a\x9eH\xb8"
        decoded = Handshake.decode(buffer)
        expected = Handshake(
            sha1_info_hash="c7e51462e85d8631c25f8c9b8c5479345a1de26b",
            peer_id="b82f51637bf2d21fd82c2a825a3639b0619e48b8",
        )
        self.assertEqual(expected, decoded)

    def test_get_address(self):
        peer = "127.0.0.1:43759"
        address = Peer._get_address(peer)
        expected = ("127.0.0.1", 43759)
        self.assertEqual(expected, address)


if __name__ == "__main__":
    unittest.main()
