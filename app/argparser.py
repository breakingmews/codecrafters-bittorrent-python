import argparse
from argparse import Namespace
from datetime import datetime


def default_filename() -> str:
    return datetime.now().strftime("./data/%Y%m%d_%H%M%S_%f")[:-3]


def parse_args() -> Namespace:
    """
    Torrent Files
    """
    parser = argparse.ArgumentParser(
        description="BitTorrent Client", prog="./your_bittorrent.sh"
    )
    subparsers = parser.add_subparsers(dest="command")

    parser_decode = subparsers.add_parser("decode", help="d3:foo3:bar5:helloi52ee")
    parser_decode.add_argument("bencoded_value", type=str)

    parser_info = subparsers.add_parser("info", help="sample.torrent")
    parser_info.add_argument("torrent_filepath", type=str)

    parser_peers = subparsers.add_parser("peers", help="sample.torrent")
    parser_peers.add_argument("torrent_filepath", type=str)

    parser_handshake = subparsers.add_parser(
        "handshake",
        help="sample.torrent <peer_ip>:<peer_port>",
    )
    parser_handshake.add_argument("torrent_filepath", type=str)
    parser_handshake.add_argument("peer_address", type=str)

    parser_download_piece = subparsers.add_parser(
        "download_piece",
        help="-o /tmp/test-piece-0 sample.torrent 0",
    )
    parser_download_piece.add_argument(
        "-o", dest="destination", type=str, default=default_filename()
    )
    parser_download_piece.add_argument("torrent_filepath", type=str)
    parser_download_piece.add_argument("piece_number", type=int)

    parser_download = subparsers.add_parser(
        "download",
        help="-o /tmp/test-piece-0 sample.torrent",
    )
    parser_download.add_argument(
        "-o", dest="destination", type=str, default=default_filename()
    )
    parser_download.add_argument("torrent_filepath", type=str)

    """
    Magnet links
    """
    parser_magnet_parse = subparsers.add_parser(
        "magnet_parse",
        help='"magnet:?xt=urn:btih:d69f91e6b2ae4c542468d1073a71d4ea13879a7f&dn=sample.torrent&tr=http://bittorrent-test-tracker.codecrafters.io/announce"',
    )
    parser_magnet_parse.add_argument("magnet_link", type=str)

    parser_magnet_info = subparsers.add_parser(
        "magnet_info",
        help='"magnet:?xt=urn:btih:d69f91e6b2ae4c542468d1073a71d4ea13879a7f&dn=sample.torrent&tr=http://bittorrent-test-tracker.codecrafters.io/announce"',
    )
    parser_magnet_info.add_argument("magnet_link", type=str)

    parser_handshake = subparsers.add_parser(
        "magnet_handshake",
        help='"magnet:?xt=urn:btih:d69f91e6b2ae4c542468d1073a71d4ea13879a7f&dn=sample.torrent&tr=http://bittorrent-test-tracker.codecrafters.io/announce"',
    )
    parser_handshake.add_argument("magnet_link", type=str)

    parser_magnet_download_piece = subparsers.add_parser(
        "magnet_download_piece",
        help="-o /tmp/test-piece-0 <magnet-link> 0",
    )
    parser_magnet_download_piece.add_argument(
        "-o", dest="destination", type=str, default=default_filename()
    )
    parser_magnet_download_piece.add_argument("magnet_link", type=str)
    parser_magnet_download_piece.add_argument("piece_number", type=int)

    parser_magnet_download = subparsers.add_parser(
        "magnet_download",
        help="-o /tmp/test-piece-0 <magnet-link>",
    )
    parser_magnet_download.add_argument(
        "-o", dest="destination", type=str, default=default_filename()
    )
    parser_magnet_download.add_argument("magnet_link", type=str)

    return parser.parse_args()
