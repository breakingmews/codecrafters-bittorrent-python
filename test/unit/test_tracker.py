import unittest

from app.bittorrent.tracker import Tracker


class TestTracker(unittest.TestCase):
    def test_encode_hash(self):
        hash_ = "d69f91e6b2ae4c542468d1073a71d4ea13879a7f"
        expected = "%d6%9f%91%e6%b2%ae%4c%54%24%68%d1%07%3a%71%d4%ea%13%87%9a%7f"
        encoded = Tracker._url_encode_hash(hash_)
        self.assertEqual(expected, encoded)
