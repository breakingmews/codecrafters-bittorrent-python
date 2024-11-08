import os
import sys
import unittest
from io import StringIO
from unittest.mock import patch

from app import main


class TestBittorrentClient(unittest.TestCase):
    TEST_DATA_DIR = os.path.join(  # type: ignore
        os.path.dirname(__file__),
        "..",
        "data",
    )

    @patch("sys.stdout", new_callable=StringIO)
    def test_decode_command(self, mock_stdout):
        # arrange
        bencoded_string = "d3:foo3:bar5:helloi52ee"
        sys.argv = ["./bittorrent.sh", "decode", bencoded_string]

        # act
        main.main()

        # assert
        actual = mock_stdout.getvalue()
        expected = '{"foo": "bar", "hello": 52}\n'
        self.assertIn(expected, actual)

    @patch("sys.stdout", new_callable=StringIO)
    def test_info_command(self, mock_stdout):
        # arrange
        filepath = os.path.join(self.TEST_DATA_DIR, "test.torrent")  # type: ignore
        sys.argv = ["./bittorrent.sh", "info", filepath]

        # act
        main.main()

        # assert
        actual = mock_stdout.getvalue()
        self.assertIn("Tracker URL:", actual)
        self.assertIn("Info Hash: c77829d2a77d6516f88cd7a3de1a26abcbfab0db", actual)
        self.assertIn("Piece Length:", actual)
        self.assertIn("Piece Hashes:", actual)

    @patch("sys.stdout", new_callable=StringIO)
    def test_peers_command(self, mock_stdout):
        # arrange
        filepath = os.path.join(self.TEST_DATA_DIR, "test.torrent")  # type: ignore
        sys.argv = ["./bittorrent.sh", "peers", filepath]

        # act
        main.main()

        # assert
        output = mock_stdout.getvalue()
        self.assertIn("Peers:", output)

    @patch("sys.stdout", new_callable=StringIO)
    def test_magnet_parse_command(self, mock_stdout):
        # arrange
        magnet_link = '"magnet:?xt=urn:btih:d69f91e6b2ae4c542468d1073a71d4ea13879a7f&dn=sample.torrent&tr=http://bittorrent-test-tracker.codecrafters.io/announce"'  # noqa
        sys.argv = ["./bittorrent.sh", "magnet_parse", magnet_link]

        # act
        main.main()

        # assert
        actual = mock_stdout.getvalue()
        self.assertIn("Tracker URL:", actual)
        self.assertIn("Info Hash: d69f91e6b2ae4c542468d1073a71d4ea13879a7f", actual)


if __name__ == "__main__":
    unittest.main()
