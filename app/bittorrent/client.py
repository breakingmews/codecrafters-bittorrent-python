import logging
import random
from typing import Tuple
from urllib.parse import parse_qs, urlparse

from app.bittorrent.peer import Peer
from app.bittorrent.tracker import Tracker
from app.dto.magnet import ExtensionHandshake, Magnet
from app.dto.peer_message import Handshake
from app.dto.torrent_file import TorrentFile

_log = logging.getLogger(__name__)


def save_file(destination: str, content: bytes):
    with open(destination, "wb") as f:
        f.write(content)
    _log.info(f"Wrote file to {destination} - {len(content)} bytes")


def download(torrent_file: TorrentFile, piece_nr: int = None, peer: Peer = None):
    if not peer:
        _log.debug(f"{torrent_file}")
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


class MagnetClient:
    @staticmethod
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

    def __init__(self, link: str):
        self.magnet = MagnetClient.parse_magnet_link(link)

        peers = Tracker.get_peers_from_magnet(self.magnet)
        self.peer = Peer(peers[random.randint(0, len(peers) - 1)])

    def do_handshake(self) -> Tuple[Handshake, ExtensionHandshake]:
        handshake = self.peer.shake_hands(
            sha1_info_hash=self.magnet.sha1_info_hash, supports_extensions=True
        )
        _log.debug(f"Handshake: {handshake}")

        self.peer.receive_bitfield()

        extension_handshake = None
        if handshake.supports_extensions:
            extension_handshake = self.peer.send_extensions_handshake()
            _log.debug(f"Extension handshake: {extension_handshake}")

        return handshake, extension_handshake

    def info(self) -> TorrentFile:
        _, extension_handshake = self.do_handshake()
        peers_metadata_extension_id = extension_handshake.peers_metadata_extension_id
        metadata = self.peer.request_metadata(peers_metadata_extension_id)
        torrent_file = TorrentFile.from_metadata(self.magnet, metadata)

        return torrent_file

    def download(self, destination, piece_nr):
        torrent_file = self.info()
        self.peer.send_interested()
        content = download(torrent_file=torrent_file, piece_nr=piece_nr, peer=self.peer)
        save_file(destination, content)
