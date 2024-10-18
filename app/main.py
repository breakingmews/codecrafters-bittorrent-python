import json
import logging

from app.bittorrent.client import (
    download,
    magnet_download,
    magnet_handshake,
    magnet_info,
    parse_magnet_link,
    save_file,
)
from app.bittorrent.codec import decode_value
from app.bittorrent.peer import Peer
from app.bittorrent.tracker import Tracker
from app.core.argparser import parse_args
from app.core.config import log_config
from app.dto.torrent_file import TorrentFile

logging.basicConfig(**log_config)
_log = logging.getLogger(__name__)


def main():
    args = parse_args()
    command = args.command

    match command:
        case "decode":
            bencoded_value = args.bencoded_value
            decoded: str = decode_value(bencoded_value)
            print(json.dumps(decoded))
            return

        case "info":
            filepath = args.torrent_filepath
            torrent_file = TorrentFile.from_file(filepath)
            print(torrent_file)

        case "peers":
            filepath = args.torrent_filepath
            torrent_file = TorrentFile.from_file(filepath)
            print(torrent_file)

            peers = Tracker.get_peers(torrent_file)
            print(f"Peers:\n{"\n".join(peers)}")

        case "handshake":
            filepath = args.torrent_filepath
            torrent_file = TorrentFile.from_file(filepath)
            print(torrent_file)

            peer_address = args.peer_address
            peer = Peer(peer_address)
            handshake = peer.shake_hands(torrent_file.sha1_info_hash)
            print(f"Peer ID: {handshake.peer_id}")

        case "download_piece":
            destination = args.destination
            filepath = args.torrent_filepath
            piece_nr = args.piece_number

            torrent_file = TorrentFile.from_file(filepath)

            content = download(torrent_file, piece_nr)
            save_file(destination, content)

        case "download":
            destination = args.destination
            filepath = args.torrent_filepath

            torrent_file = TorrentFile.from_file(filepath)

            content = download(torrent_file)
            save_file(destination, content)

        case "magnet_parse":
            magnet_link = args.magnet_link
            magnet = parse_magnet_link(magnet_link)
            print(f"Tracker URL: {magnet.tracker}")
            print(f"Info Hash: {magnet.info_hash}")

        case "magnet_handshake":
            magnet_link = args.magnet_link

            handshake, extension_handshake = magnet_handshake(magnet_link)
            print(
                f"Peer Metadata Extension ID: {extension_handshake.peers_metadata_extension_id}"
            )
            print(f"Peer ID: {handshake.peer_id}")

        case "magnet_info":
            magnet_link = args.magnet_link

            torrent_file = magnet_info(magnet_link)
            print(torrent_file)

        case "magnet_download_piece":
            destination = args.destination
            magnet_link = args.magnet_link
            piece_nr = args.piece_number

            magnet_download(destination, magnet_link, piece_nr)

        case "magnet_download":
            destination = args.destination
            magnet_link = args.magnet_link
            piece_nr = None

            magnet_download(destination, magnet_link, piece_nr)


if __name__ == "__main__":
    main()
