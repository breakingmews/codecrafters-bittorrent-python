import unittest
from app.main import decode_bencode


class TestMain(unittest.TestCase):
    def test_decode_bencode_str_1(self):
        decoded = decode_bencode(b"5:hello")
        expected = b"hello"
        self.assertEqual(expected, decoded)

    def test_decode_bencode_str_2(self):
        decoded = decode_bencode(b"10:hello12345")
        expected = b"hello12345"
        self.assertEqual(expected, decoded)

    def test_decode_bencode_int(self):
        decoded = decode_bencode(b"i52e")
        expected = 52
        self.assertEqual(expected, decoded)

    def test_decode_bencode_list(self):
        decoded = decode_bencode(b"l5:helloi52ee")
        expected = [b"hello", 52]
        self.assertEqual(expected, decoded)



if __name__ == '__main__':
    unittest.main()
