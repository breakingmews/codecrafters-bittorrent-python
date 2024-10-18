import os
import unittest

from app.dto.torrent_file import Block, TorrentFile


class TestTorrentFile(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.TEST_DATA_DIR = os.path.join(
            os.path.dirname(__file__),
            "..",
            "data",
        )

    def test_decode_torrent_file(self):
        # arrange
        filepath = os.path.join(self.TEST_DATA_DIR, "test.torrent")

        # act
        file = TorrentFile.from_file(filepath)
        info_hash = "1cad4a486798d952614c394eb15e75bec587fd08"
        sha1_info_hash = b"\x1c\xadJHg\x98\xd9RaL9N\xb1^u\xbe\xc5\x87\xfd\x08"

        # assert
        self.assertEqual(dict, type(file.content))

        expected_info_hash = (
            b"\xc7x)\xd2\xa7}e\x16\xf8\x8c\xd7\xa3\xde\x1a&\xab\xcb\xfa\xb0\xdb"
        )
        self.assertEqual(expected_info_hash, file.sha1_info_hash)

        expected_piece_sizes = 11 * [262144] + [110536]
        expected_hashes = [
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
        for i, piece in enumerate(file.pieces):
            self.assertEqual(expected_piece_sizes[i], piece.size)
            self.assertEqual(expected_hashes[i], piece.hash_)

    def test_decode_torrent_file_congratulations(self):
        # arrange
        filepath = os.path.join(self.TEST_DATA_DIR, "congratulations.torrent")

        # act
        file = TorrentFile.from_file(filepath)

        # assert
        expected_piece_sizes = 3 * [262144] + [34460]
        expected_last_block = Block(ix=2, offset=2 * 16 * 1024, size=1692)

        for i, piece in enumerate(file.pieces):
            self.assertEqual(expected_piece_sizes[i], piece.size)

        self.assertEqual(expected_last_block, file.pieces[-1].blocks[-1])


if __name__ == "__main__":
    unittest.main()
