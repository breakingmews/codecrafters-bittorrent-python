import unittest

from app.bittorrent.codec import decode_value


class TestCodec(unittest.TestCase):
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
