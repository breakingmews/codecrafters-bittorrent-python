import logging
import random
from urllib.parse import parse_qs, urlparse

from app.dto.magnet import Magnet
from app.dto.torrent_file import TorrentFile
from app.peer import Peer
from app.tracker import Tracker

_log = logging.getLogger(__name__)


def save_file(destination: str, content: bytes):
    with open(destination, "wb") as f:
        f.write(content)
    _log.info(f"Wrote file to {destination} - {len(content)} bytes")


def download(torrent_file: TorrentFile, piece_nr: int = None, peer: Peer = None):
    if not peer:
        _log.debug(f"\n{torrent_file}")
        peers = Tracker.get_peers(torrent_file)
        _log.debug(f"\nPeers:\n{"\n".join(peers)}")

        peer = Peer(peers[random.randint(0, len(peers) - 1)])
        peer.shake_hands(torrent_file.sha1_info_hash)
        peer.receive_bitfield()
        peer.send_interested()

    pieces = []
    if piece_nr is not None:
        piece = peer.request_piece(torrent_file, piece_nr)
        pieces.append(piece)
    else:
        for ix in range(len(torrent_file.pieces)):
            piece = peer.request_piece(torrent_file, ix)
            pieces.append(piece)

    content = b"".join(pieces)
    return content


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
