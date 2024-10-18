import json
import logging
import random

from app.argparser import parse_args
from app.client import download, parse_magnet_link, save_file
from app.codec import decode_value
from app.config import log_config
from app.dto.torrent_file import TorrentFile
from app.peer import Peer
from app.tracker import Tracker

logging.basicConfig(**log_config)
_log = logging.getLogger(__name__)


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
