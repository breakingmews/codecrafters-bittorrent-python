import json
import random
import sys

from app.client import download, parse_magnet_link, save_file
from app.codec import decode_value
from app.dto.torrent_file import TorrentFile
from app.peer import Peer
from app.tracker import Tracker


def main():
    # TODO smart argparse
    command = sys.argv[1]
    commands = [
        "decode",
        "info",
        "peers",
        "handshake",
        "download_piece",
        "download",
        "magnet_parse",
        "magnet_handshake",
        "magnet_info"
    ]

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
            handshake = peer.shake_hands(torrent_file.sha1_info_hash)
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

    # ./your_bittorrent.sh magnet_handshake magnet:?xt=urn:btih:d69f91e6b2ae4c542468d1073a71d4ea13879a7f&dn=sample.torrent&tr=http%3A%2F%2Fbittorrent-test-tracker.codecrafters.io%2Fannounce
    if command in ("magnet_handshake", "magnet_info"):
        magnet_link = sys.argv[2]
        magnet = parse_magnet_link(magnet_link)
        peers = Tracker.get_peers_from_magnet(magnet)
        print(f"Peers:\n{"\n".join(peers)}")

        peer = Peer(peers[random.randint(0, len(peers) - 1)])
        handshake = peer.shake_hands(sha1_info_hash=magnet.sha1_info_hash, supports_extensions=True)
        print(f"Peer ID: {handshake.peer_id}")

        if handshake.supports_extensions:
            extension_handshake = peer.send_extensions_handshake()
            peers_metadata_extension_id = extension_handshake.payload[b"m"][b"ut_metadata"]
            print(f"Extension handshake: {extension_handshake}")
            print(f"Peer Metadata Extension ID: {peers_metadata_extension_id}")

            if command == "magnet_info":
                peer.send_request_extension(peers_metadata_extension_id)


if __name__ == "__main__":
    main()
