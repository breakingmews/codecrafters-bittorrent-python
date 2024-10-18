import unittest

from app.bittorrent.peer import Peer


class TestPeer(unittest.TestCase):
    def test_get_address(self):
        # arrange
        peer = "127.0.0.1:43759"

        # act
        address = Peer._get_address(peer)

        # assert
        expected = ("127.0.0.1", 43759)
        self.assertEqual(expected, address)
