import unittest
from app.main import decode_value


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
        expected = {"foo":"bar","hello":52}
        self.assertEqual(expected, decoded)

    @unittest.skip("Test file generator")
    def test1(self):
        content = b"d8:announce55:http://bittorrent-test-tracker.codecrafters.io/announce10:created by13:mktorrent 1.14:infod6:lengthi2994120e4:name12:codercat.gif12:piece lengthi262144e6:pieces240:<40\x9f\xae\xbf\x01\xe4\x9c\x0fc\xc9\x0b~\xdc\xc2%\x9bj\xd0\xb8Q\x9b.\xa9\xbb7?\xf5g\xf6DB\x81V\xc9\x8a\x1d\x00\xfc\x9d\xc8\x13fXu6\xf4\x8c \x98\xa1\xd7\x96\x92\xf2Y\x0f\xd9\xa6\x03<a\xe7\x17\xf8\xc0\xd1\xe5XPh\x0e\xb4Q\xe3T;b\x03oT\xe7F\xec6\x9fe\xf3-E\xf7{\x1f\x1c7b\x1f\xb9e\xc6VpKx\x10~\xd5S\xbd\x08\x13\xf9/\xefx\x02g\xc0{t1\xb8h17\xd2\x0f\xf5\x94\xb1\xf1\xbf?\x885\x16]h\xfb\x042\xbd\x8ew\x96\x08\xd2w\x82\xb7y\xc7s\x80b\xe9\xb5\n\xb5\xd6\xbc\x04\t\xa0\xf3\xa9P8Wf\x9dG\xfeu-Ew\xea\x00\xa8n\xe6\xab\xbc0\xcd\xdb\x80\n\x0bb\xd7\xa2\x96\x11\x11f\xd89x?R\xb7\x0f\x0c\x90-V\x19k\xd3\xee\x7f7\x9b]\xb5~;=\x8d\xb9\xe3M\xb6;K\xa1\xbe'\x93\t\x11\xaa7\xb3\xf9\x97\xddee"
        import bencodepy
        with open("test1.torrent", "wb") as f:
            bencodepy.bwrite(content, f)




if __name__ == '__main__':
    unittest.main()
