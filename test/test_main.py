import unittest

from app.main import decode_value, decode_file, parse_hashes, encode_hash


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
        content = decode_file(filepath)
        self.assertEqual(dict, type(content))

    def test_parse_hashes(self):
        # arrange
        filepath = "test.torrent"
        decoded = decode_file(filepath)
        info = decoded[b"info"]

        # act
        hashes = parse_hashes(info)

        # assert
        expected = "3c34309faebf01e49c0f63c90b7edcc2259b6ad0\nb8519b2ea9bb373ff567f644428156c98a1d00fc\n9dc81366587536f48c2098a1d79692f2590fd9a6\n033c61e717f8c0d1e55850680eb451e3543b6203\n6f54e746ec369f65f32d45f77b1f1c37621fb965\nc656704b78107ed553bd0813f92fef780267c07b\n7431b8683137d20ff594b1f1bf3f8835165d68fb\n0432bd8e779608d27782b779c7738062e9b50ab5\nd6bc0409a0f3a9503857669d47fe752d4577ea00\na86ee6abbc30cddb800a0b62d7a296111166d839\n783f52b70f0c902d56196bd3ee7f379b5db57e3b\n3d8db9e34db63b4ba1be27930911aa37b3f997dd\n"
        self.assertEqual(expected, hashes)

    def test_encode_hash(self):
        hash_ = "d69f91e6b2ae4c542468d1073a71d4ea13879a7f"
        expected = "%d6%9f%91%e6%b2%ae%4c%54%24%68%d1%07%3a%71%d4%ea%13%87%9a%7f"
        encoded = encode_hash(hash_)
        self.assertEqual(expected, encoded)


if __name__ == '__main__':
    unittest.main()
