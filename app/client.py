import random
import traceback
from urllib.parse import parse_qs, urlparse

from app.dto.magnet import Magnet
from app.dto.torrent_file import TorrentFile
from app.peer import Peer
from app.tracker import Tracker


def save_file(destination: str, content: bytes):
    with open(destination, "wb") as f:
        f.write(content)
    print(f"Wrote file to {destination}")


def download(torrent_file: TorrentFile, piece_nr: int = None):
    # print(f"\n{torrent_file}")
    peers = Tracker.get_peers(torrent_file)
    # print(f"\nPeers:\n{"\n".join(peers)}")

    peer = Peer(peers[random.randint(0, len(peers) - 1)])
    try:
        peer.shake_hands(torrent_file.sha1_info_hash)
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


def parse_magnet_link(link: str):
    """
    Example of magnet link:
    magnet:?xt=urn:btih:d69f91e6b2ae4c542468d1073a71d4ea13879a7f&dn=sample.torrent&tr=http%3A%2F%2Fbittorrent-test-tracker.codecrafters.io%2Fannounce
    """
    parsed = parse_qs(urlparse(link).query)
    info_hash = parsed["xt"][0].replace("urn:btih:", "")
    filename = parsed["dn"][0]
    tracker = parsed["tr"][0]
    magnet = Magnet(info_hash, filename, tracker)
    return magnet
