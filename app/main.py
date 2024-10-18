import json
import sys

from app.client import download, save_file, parse_magnet_link
from app.codec import decode_value
from app.dto.torrent_file import TorrentFile
from app.peer import Peer
from app.tracker import Tracker


def main():
    # TODO smart argparse
    command = sys.argv[1]
    commands = ["decode", "info", "peers", "handshake", "download_piece", "download", "magnet_parse"]

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
        torrent_file = TorrentFile(filepath)
        print(torrent_file)

        # ./your_bittorrent.sh info sample.torrent
        if command == "info":
            return

        # ./your_bittorrent.sh peers sample.torrent
        if command == "peers":
            peers = Tracker.get_peers(torrent_file)
            print(f"Peers:\n{"\n".join(peers)}")

        # ./your_bittorrent.sh handshake sample.torrent <peer_ip>:<peer_port>
        if command == "handshake":
            peer_address = sys.argv[3]
            peer = Peer(peer_address)
            handshake = peer.shake_hands(torrent_file)
            print(f"Peer ID: {handshake.peer_id}")

    # ./your_bittorrent.sh download_piece -o /tmp/test-piece-0 sample.torrent 0
    if command == "download_piece":
        destination = sys.argv[3]
        filepath = sys.argv[4]
        piece_nr = int(sys.argv[5])

        torrent_file = TorrentFile(filepath)

        content = download(torrent_file, piece_nr)
        save_file(destination, content)

    # ./your_bittorrent.sh download -o /tmp/test.txt sample.torrent
    if command == "download":
        destination = sys.argv[3]
        filepath = sys.argv[4]

        torrent_file = TorrentFile(filepath)

        content = download(torrent_file)
        save_file(destination, content)

    # ./your_bittorrent.sh magnet_parse magnet:?xt=urn:btih:d69f91e6b2ae4c542468d1073a71d4ea13879a7f&dn=sample.torrent&tr=http%3A%2F%2Fbittorrent-test-tracker.codecrafters.io%2Fannounce
    if command == "magnet_parse":
        magnet_link = sys.argv[2]
        magnet = parse_magnet_link(magnet_link)
        print(f"Tracker URL: {magnet.tracker}")
        print(f"Info Hash: {magnet.info_hash}")


if __name__ == "__main__":
    main()
