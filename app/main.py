import argparse
import json
import logging
import os
import random
from argparse import Namespace
from datetime import datetime

from app.client import download, parse_magnet_link, save_file
from app.codec import decode_value
from app.config import log_config
from app.dto.torrent_file import TorrentFile
from app.peer import Peer
from app.tracker import Tracker

logging.basicConfig(**log_config)
_log = logging.getLogger(__name__)


def valid_path(path):
    if not os.path.exists(path):
        raise argparse.ArgumentTypeError(f"'{path}' is not a valid path")
    return path


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

    parser_decode = subparsers.add_parser(
        "decode", help="d3:foo3:bar5:helloi52ee"
    )
    parser_decode.add_argument("bencoded_value", type=str)

    parser_info = subparsers.add_parser(
        "info", help="sample.torrent"
    )
    parser_info.add_argument("torrent_filepath", type=valid_path)

    parser_peers = subparsers.add_parser(
        "peers", help="sample.torrent"
    )
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
    parser_download_piece.add_argument("-o", dest="destination", type=str, default=default_filename())
    parser_download_piece.add_argument("torrent_filepath", type=str)
    parser_download_piece.add_argument("piece_number", type=int)

    parser_download = subparsers.add_parser(
        "download",
        help="-o /tmp/test-piece-0 sample.torrent",
    )
    parser_download.add_argument("-o", dest="destination", type=str, default=default_filename())
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
    parser_magnet_download_piece.add_argument("-o", dest="destination", type=valid_path, default=default_filename())
    parser_magnet_download_piece.add_argument("magnet_link", type=str)
    parser_magnet_download_piece.add_argument("piece_number", type=int)

    parser_magnet_download = subparsers.add_parser(
        "magnet_download",
        help="-o /tmp/test-piece-0 <magnet-link>",
    )
    parser_magnet_download.add_argument("-o", dest="destination", type=valid_path, default=default_filename())
    parser_magnet_download.add_argument("magnet_link", type=str)

    return parser.parse_args()


def main():
    args = parse_args()
    command = args.command

    if command == "decode":
        bencoded_value = args.bencoded_value
        decoded: str = decode_value(bencoded_value)
        print(json.dumps(decoded))
        return

    if command in ("info", "peers", "handshake"):
        filepath = args.torrent_filepath
        torrent_file = TorrentFile.from_file(filepath)
        print(torrent_file)

        if command == "info":
            return

        if command == "peers":
            peers = Tracker.get_peers(torrent_file)
            print(f"Peers:\n{"\n".join(peers)}")

        if command == "handshake":
            peer_address = args.peer_address
            peer = Peer(peer_address)
            handshake = peer.shake_hands(torrent_file.sha1_info_hash)
            print(f"Peer ID: {handshake.peer_id}")

    if command == "download_piece":
        destination = args.destination
        filepath = args.torrent_filepath
        piece_nr = args.piece_number

        torrent_file = TorrentFile.from_file(filepath)

        content = download(torrent_file, piece_nr)
        save_file(destination, content)

    if command == "download":
        destination = args.destination
        filepath = args.torrent_filepath

        torrent_file = TorrentFile.from_file(filepath)

        content = download(torrent_file)
        save_file(destination, content)

    if command == "magnet_parse":
        magnet_link = args.magnet_link
        magnet = parse_magnet_link(magnet_link)
        print(f"Tracker URL: {magnet.tracker}")
        print(f"Info Hash: {magnet.info_hash}")

    if command in ("magnet_handshake", "magnet_info"):
        magnet_link = args.magnet_link
        magnet = parse_magnet_link(magnet_link)
        peers = Tracker.get_peers_from_magnet(magnet)

        peer = Peer(peers[random.randint(0, len(peers) - 1)])
        handshake = peer.shake_hands(
            sha1_info_hash=magnet.sha1_info_hash, supports_extensions=True
        )

        if handshake.supports_extensions:
            extension_handshake = peer.send_extensions_handshake()
            peers_metadata_extension_id = (
                extension_handshake.peers_metadata_extension_id
            )
            _log.debug(f"Extension handshake: {extension_handshake}")
            if command == "magnet_handshake":
                print(f"Peer Metadata Extension ID: {peers_metadata_extension_id}")
                print(f"Peer ID: {handshake.peer_id}")
                _log.debug(f"Peers:\n{"\n".join(peers)}")

            if command == "magnet_info":
                metadata = peer.request_metadata(peers_metadata_extension_id)
                torrent_file = TorrentFile.from_metadata(magnet, metadata)
                print(torrent_file)

    if command == "magnet_download_piece":
        destination = args.destination
        magnet_link = args.magnet_link
        piece_nr = args.piece_number

        magnet = parse_magnet_link(magnet_link)
        peers = Tracker.get_peers_from_magnet(magnet)

        peer = Peer(peers[random.randint(0, len(peers) - 1)])
        handshake = peer.shake_hands(
            sha1_info_hash=magnet.sha1_info_hash, supports_extensions=True
        )

        if handshake.supports_extensions:
            extension_handshake = peer.send_extensions_handshake()

            peer.send_interested()

            peers_metadata_extension_id = (
                extension_handshake.peers_metadata_extension_id
            )

            metadata = peer.request_metadata(peers_metadata_extension_id)
            torrent_file = TorrentFile.from_metadata(magnet, metadata)

            content = download(torrent_file, piece_nr, peer)
            save_file(destination, content)

    if command == "magnet_download":
        destination = args.destination
        magnet_link = args.magnet_link

        magnet = parse_magnet_link(magnet_link)
        peers = Tracker.get_peers_from_magnet(magnet)

        peer = Peer(peers[random.randint(0, len(peers) - 1)])
        handshake = peer.shake_hands(
            sha1_info_hash=magnet.sha1_info_hash, supports_extensions=True
        )

        if handshake.supports_extensions:
            extension_handshake = peer.send_extensions_handshake()
            peer.send_interested()
            peers_metadata_extension_id = (
                extension_handshake.peers_metadata_extension_id
            )

            metadata = peer.request_metadata(peers_metadata_extension_id)
            torrent_file = TorrentFile.from_metadata(magnet, metadata)

            content = download(torrent_file, piece_nr=None, peer=peer)
            save_file(destination, content)


if __name__ == "__main__":
    main()
