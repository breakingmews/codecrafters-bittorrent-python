import json
import random
import sys
import traceback

from app.codec import decode_value
from app.dto.torrent_file import TorrentFile
from app.peer import Peer
from app.tracker import Tracker


def save_piece(destination: str, piece_block: bytes):
    with open(destination, "wb") as f:
        f.write(piece_block)
    print(f"Wrote piece block to {destination}")


def download_piece(destination: str, torrent_filepath: str, piece_nr: int):
    print(f"{destination}, {torrent_filepath}, {piece_nr}")
    torrent_file = TorrentFile(torrent_filepath)
    print(f"\n{torrent_file}")

    peers = Tracker.get_peers(torrent_file)
    print(f"\nPeers:\n{"\n".join(peers)}")

    peer = Peer(peers[random.randint(0, len(peers) - 1)])
    try:
        handshake, bitfield = peer.shake_hands(torrent_file)
        print(f"\nPeer ID: {handshake.peer_id}")

        unchoke = peer.interested()
        print(f"Unchoke: {unchoke}")

        blocks = peer.request_piece(torrent_file, piece_nr)
        print(f"Piece: {blocks}")

        save_piece(destination, b"\n".join(blocks))
    except Exception:
        print(f"Error: {traceback.format_exc()}")
    finally:
        print("Closing connection")
        peer.socket.close()


def main():
    # TODO smart argparse
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
            handshake, _ = peer.shake_hands(torrent_file)
            print(f"Peer ID: {handshake.peer_id}")

    # ./your_bittorrent.sh download_piece -o /tmp/test-piece-0 sample.torrent 0
    if command == "download_piece":
        destination = sys.argv[3]
        filepath = sys.argv[4]
        piece_nr = int(sys.argv[5])

        download_piece(destination, filepath, piece_nr)


if __name__ == "__main__":
    main()
