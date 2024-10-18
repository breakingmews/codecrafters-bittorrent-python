import unittest

from app.dto.magnet import Data, ExtensionHandshake
from app.dto.peer_message import BitField, Handshake, Interested, Unchoke


class TestPeerMessages(unittest.TestCase):
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

    def test_decode_bitfield(self):
        buffer = b"\x00\x00\x00\x03\x05\x03\x03"
        decoded = BitField.decode(buffer)
        expected = BitField(
            id_=5, length=3, payload=(0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1)
        )
        self.assertEqual(expected, decoded)

    def test_encode_interested(self):
        encoded = Interested().encode()
        expected = b"\x00\x00\x00\x01\x02"
        self.assertEqual(expected, encoded)

    @unittest.skip("Not implemented")
    def test_parse_handshake_response(self):
        response = b"\x13BitTorrent protocol\x00\x00\x00\x00\x00\x00\x00\x04\xc7x)\xd2\xa7}e\x16\xf8\x8c\xd7\xa3\xde\x1a&\xab\xcb\xfa\xb0\xdb-RN0.0.0-\xcaBQ\xd1\x916\xb3\xf7x;\x89\x00\x00\x00\x03\x05\xff\xf0"

    def test_decode_unchoke(self):
        buffer = b"\x00\x00\x00\x01\x01"
        decoded = Unchoke.decode(buffer)
        expected = Unchoke(id_=1, length=1)
        self.assertEqual(expected, decoded)

    @unittest.skip("Not implemented")
    def test_decode_extensions_handshake(self):
        buffer = b"\x00\x00\x00\x02\x05\xe0\x00\x00\x001\x14\x00d1:md11:ut_metadatai161ee13:metadata_sizei132ee"
        # buffer = b'\x00\x001\x14\x00d1:md11:ut_metadatai248ee13:metadata_sizei132ee'
        decoded = ExtensionHandshake.decode(buffer)

        self.assertEqual(decoded.extension_message_id, 0)
        self.assertEqual(decoded.id_, 20)
        self.assertEqual(decoded.length, 49)
        self.assertEqual(
            decoded.payload, {b"m": {b"ut_metadata": 161}, b"metadata_size": 132}
        )

    def test_decode_metadata_response(self):
        buffer = b"\x00\x00\x00\xb1\x14\x10d8:msg_typei1e5:piecei0e10:total_sizei132eed6:lengthi636505e4:name11:magnet1.gif12:piece lengthi262144e6:pieces60:;F\xa9m\x9b\xc3qm\x1bu\xda\x91\xe6\xd7S\xa7\x93\xad\x1c\xef\xed\xa4\x17\xcb\\\x1c\xdb\xf8A\x12\\A-\xa0\xbe\xc9\xdb\x83\x01\xf3B/E\xb1\x05.-E\xda>*e\x16\xe1\xbb\x1f\x1d\xb0\x073e"
        metadata: Data = Data.decode(buffer)
        self.assertEqual(dict, type(metadata.payload))
