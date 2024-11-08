import json
import logging

from app.bittorrent.client import (
    MagnetClient,
    download,
    save_file,
)
from app.bittorrent.codec import decode_value
from app.bittorrent.peer import Peer
from app.bittorrent.tracker import Tracker
from app.core.argparser import parse_args
from app.core.config import log_config
from app.core.const import Command
from app.dto.torrent_file import TorrentFile

logging.basicConfig(**log_config)  # type: ignore[arg-type]
_log = logging.getLogger(__name__)


def main():
    args = parse_args()

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG if args.verbose else logging.INFO)

    command = Command(args.command)

    match command:
        case Command.DECODE:
            bencoded_value = args.bencoded_value
            decoded: str = decode_value(bencoded_value)
            print(json.dumps(decoded))
            return

        case Command.INFO:
            filepath = args.torrent_filepath
            torrent_file = TorrentFile.from_file(filepath)
            print(torrent_file)

        case Command.PEERS:
            filepath = args.torrent_filepath
            torrent_file = TorrentFile.from_file(filepath)
            print(torrent_file)

            peers = Tracker.get_peers(torrent_file)
            print(f"Peers:\n{"\n".join(peers)}")

        case Command.HANDSHAKE:
            filepath = args.torrent_filepath
            torrent_file = TorrentFile.from_file(filepath)
            print(torrent_file)

            peer_address = args.peer_address
            peer = Peer(peer_address)
            handshake = peer.shake_hands(torrent_file.sha1_info_hash)
            print(f"Peer ID: {handshake.peer_id}")

        case Command.DOWNLOAD_PIECE:
            destination = args.destination
            filepath = args.torrent_filepath
            piece_nr = args.piece_number

            torrent_file = TorrentFile.from_file(filepath)

            content = download(torrent_file, piece_nr)
            save_file(destination, content)

        case Command.DOWNLOAD:
            destination = args.destination
            filepath = args.torrent_filepath

            torrent_file = TorrentFile.from_file(filepath)

            content = download(torrent_file)
            save_file(destination, content)

        case Command.MAGNET_PARSE:
            magnet_link = args.magnet_link
            magnet = MagnetClient.parse_magnet_link(magnet_link)
            print(f"Tracker URL: {magnet.tracker}")
            print(f"Info Hash: {magnet.info_hash}")

        case Command.MAGNET_HANDSHAKE:
            magnet_link = args.magnet_link

            magnet = MagnetClient(magnet_link)
            handshake, extension_handshake = magnet.do_handshake()
            print(
                f"Peer Metadata Extension ID: {extension_handshake.peers_metadata_extension_id}"
            )
            print(f"Peer ID: {handshake.peer_id}")

        case Command.MAGNET_INFO:
            magnet_link = args.magnet_link

            magnet = MagnetClient(magnet_link)
            torrent_file = magnet.info()
            print(torrent_file)

        case Command.MAGNET_DOWNLOAD_PIECE:
            destination = args.destination
            magnet_link = args.magnet_link
            piece_nr = args.piece_number

            magnet = MagnetClient(magnet_link)
            magnet.download(destination, piece_nr)

        case Command.MAGNET_DOWNLOAD:
            destination = args.destination
            magnet_link = args.magnet_link
            piece_nr = None

            magnet = MagnetClient(magnet_link)
            magnet.download(destination, piece_nr)


if __name__ == "__main__":
    main()
