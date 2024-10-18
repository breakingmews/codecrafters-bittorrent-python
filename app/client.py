import random
import traceback

from app.dto.torrent_file import TorrentFile
from app.peer import Peer
from app.tracker import Tracker


def save_file(destination: str, content: bytes):
    with open(destination, "wb") as f:
        f.write(content)
    print(f"Wrote file to {destination}")


def download(torrent_file: TorrentFile, piece_nr: int = None):
    print(f"\n{torrent_file}")

    peers = Tracker.get_peers(torrent_file)
    print(f"\nPeers:\n{"\n".join(peers)}")

    peer = Peer(peers[random.randint(0, len(peers) - 1)])
    try:
        peer.shake_hands(torrent_file)
        peer.receive_bitfield()
        peer.send_interested()

        pieces = []
        if piece_nr:
            piece = peer.request_piece(torrent_file, piece_nr)
            pieces.append(piece)
        else:
            for ix in range(len(torrent_file.pieces)):
                piece = peer.request_piece(torrent_file, ix)
                pieces.append(piece)

        content = b"".join(pieces)
        return content
    except Exception:
        print(f"Error: {traceback.format_exc()}")
    finally:
        print("Closing connection")
        peer.socket.close()
