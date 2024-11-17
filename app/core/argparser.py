import argparse
from argparse import Namespace
from datetime import datetime

from .const import Command


def default_filename() -> str:
    return datetime.now().strftime("./data/%Y%m%d_%H%M%S_%f")[:-3]


def parse_args() -> Namespace:
    sample_magnet_link = '"magnet:?xt=urn:btih:d69f91e6b2ae4c542468d1073a71d4ea13879a7f&dn=sample.torrent&tr=http://bittorrent-test-tracker.codecrafters.io/announce"'  # noqa

    parser = argparse.ArgumentParser(
        description="BitTorrent Client", prog="./bittorrent.sh"
    )
    parser.add_argument(
        "-v", dest="verbose", action="store_true", help="verbose output"
    )
    subparsers = parser.add_subparsers(dest="command")

    parser_decode = subparsers.add_parser(
        Command.DECODE.value, help="Decode bencoded value"
    )
    parser_decode.add_argument(
        "bencoded_value", type=str, help="E.g. d3:foo3:bar5:helloi52ee"
    )

    parser_info = subparsers.add_parser(
        Command.INFO.value, help="Show torrent file info"
    )
    parser_info.add_argument("torrent_filepath", type=str, help="./data/sample.torrent")

    parser_peers = subparsers.add_parser(Command.PEERS.value, help="Discover peers")
    parser_peers.add_argument(
        "torrent_filepath", type=str, help="./data/sample.torrent"
    )

    parser_handshake = subparsers.add_parser(
        Command.HANDSHAKE.value,
        help="Complete a handshake with peer",
    )
    parser_handshake.add_argument(
        "torrent_filepath", type=str, help="./data/sample.torrent"
    )
    parser_handshake.add_argument(
        "peer_address", type=str, help="<peer_ip>:<peer_port>"
    )

    parser_download_piece = subparsers.add_parser(
        Command.DOWNLOAD_PIECE.value,
        help="Download a file piece using torrent file",
    )
    parser_download_piece.add_argument(
        "-o",
        dest="destination",
        type=str,
        default=default_filename(),
        help="/Downloads/test-piece-0",
    )
    parser_download_piece.add_argument(
        "torrent_filepath", type=str, help=" ./data/sample.torrent"
    )
    parser_download_piece.add_argument("piece_number", type=int, help="0")

    parser_download = subparsers.add_parser(
        Command.DOWNLOAD.value,
        help="Download a file using torrent file",
    )
    parser_download.add_argument(
        "-o",
        dest="destination",
        type=str,
        default=default_filename(),
        help="/Downloads/test-piece-0",
    )
    parser_download.add_argument(
        "torrent_filepath", type=str, help="./data/sample.torrent"
    )

    """
    Magnet links
    """
    parser_magnet_parse = subparsers.add_parser(
        Command.MAGNET_PARSE.value,
        help="Parse magnet link",
    )
    parser_magnet_parse.add_argument("magnet_link", type=str, help=sample_magnet_link)

    parser_magnet_info = subparsers.add_parser(
        Command.MAGNET_INFO.value,
        help="Request metadata extension",
    )
    parser_magnet_info.add_argument("magnet_link", type=str, help=sample_magnet_link)

    parser_handshake = subparsers.add_parser(
        Command.MAGNET_HANDSHAKE.value,
        help="Complete extension handshake with peer",
    )
    parser_handshake.add_argument("magnet_link", type=str, help=sample_magnet_link)

    parser_magnet_download_piece = subparsers.add_parser(
        Command.MAGNET_DOWNLOAD_PIECE.value,
        help="Download a file piece using magnet link",
    )
    parser_magnet_download_piece.add_argument(
        "-o",
        dest="destination",
        type=str,
        default=default_filename(),
        help="/Downloads/test-piece-0",
    )
    parser_magnet_download_piece.add_argument(
        "magnet_link", type=str, help=sample_magnet_link
    )
    parser_magnet_download_piece.add_argument("piece_number", type=int, help="0")

    parser_magnet_download = subparsers.add_parser(
        Command.MAGNET_DOWNLOAD.value,
        help="Download a file using magnet link",
    )
    parser_magnet_download.add_argument(
        "-o",
        dest="destination",
        type=str,
        default=default_filename(),
        help="/Downloads/test-piece-0",
    )
    parser_magnet_download.add_argument(
        "magnet_link", type=str, help=sample_magnet_link
    )

    return parser.parse_args()
