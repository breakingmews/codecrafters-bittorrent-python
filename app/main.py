import json
import sys

from app.client import do_handshake, get_peers
from app.codec import decode_value
from app.dto import Handshake, TorrentFile


def main():
    command = sys.argv[1]
    commands = ["decode", "info", "peers", "handshake", "download_piece"]

    if command not in commands:
        raise NotImplementedError(f"Unknown command {command}")

    # ./your_bittorrent.sh decode d3:foo3:bar5:helloi52ee
    if command == "decode":
        bencoded_value = sys.argv[2]
        decoded: str = decode_value(bencoded_value)
        print(json.dumps(decoded))
        return

    if command in ("info", "peers", "handshake"):
        filepath = sys.argv[2]
        torrent_file = TorrentFile.read(filepath).decode()
        print(torrent_file)

        # ./your_bittorrent.sh info sample.torrent
        if command == "info":
            return

        # ./your_bittorrent.sh peers sample.torrent
        if command == "peers":
            peers = get_peers(
                torrent_file.tracker,
                torrent_file.sha1_info_hash.hex(),
                torrent_file.length,
            )
            print("\n".join(peers))

        # ./your_bittorrent.sh handshake sample.torrent <peer_ip>:<peer_port>
        if command == "handshake":
            peer = sys.argv[3]
            handshake: Handshake = do_handshake(peer, torrent_file.sha1_info_hash)
            print(f"Peer ID: {handshake.peer_id}")

    # ./your_bittorrent.sh download_piece -o /tmp/test-piece-0 sample.torrent 0
    if command == "download_piece":
        destination = sys.argv[3]
        filepath = sys.argv[4]
        piece_nr = sys.argv[5]
        print(f"Piece nr: {piece_nr}")

        torrent_file = TorrentFile.read(filepath).decode()
        print(torrent_file)
        raise NotImplementedError(f"{command} not implemented")


if __name__ == "__main__":
    main()
