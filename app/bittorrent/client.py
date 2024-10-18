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


def magnet_info(magnet_link: str) -> TorrentFile:
    magnet = parse_magnet_link(magnet_link)
    peers = Tracker.get_peers_from_magnet(magnet)

    peer = Peer(peers[random.randint(0, len(peers) - 1)])
    handshake = peer.shake_hands(
        sha1_info_hash=magnet.sha1_info_hash, supports_extensions=True
    )
    _log.debug(f"Handshake: {handshake}")

    metadata = None
    if handshake.supports_extensions:
        extension_handshake = peer.send_extensions_handshake()
        _log.debug(f"Extension handshake: {extension_handshake}")

        peers_metadata_extension_id = extension_handshake.peers_metadata_extension_id
        metadata = peer.request_metadata(peers_metadata_extension_id)
    torrent_file = TorrentFile.from_metadata(magnet, metadata)

    return torrent_file


def magnet_handshake(magnet_link: str) -> Tuple[Handshake, ExtensionHandshake]:
    magnet = parse_magnet_link(magnet_link)
    peers = Tracker.get_peers_from_magnet(magnet)

    peer = Peer(peers[random.randint(0, len(peers) - 1)])
    handshake = peer.shake_hands(
        sha1_info_hash=magnet.sha1_info_hash, supports_extensions=True
    )
    _log.debug(f"Handshake: {handshake}")

    extension_handshake = None
    if handshake.supports_extensions:
        extension_handshake = peer.send_extensions_handshake()
        _log.debug(f"Extension handshake: {extension_handshake}")

    return handshake, extension_handshake


def magnet_download(destination, magnet_link, piece_nr):
    magnet = parse_magnet_link(magnet_link)
    peers = Tracker.get_peers_from_magnet(magnet)

    peer = Peer(peers[random.randint(0, len(peers) - 1)])
    handshake = peer.shake_hands(
        sha1_info_hash=magnet.sha1_info_hash, supports_extensions=True
    )
    _log.debug(f"Handshake: {handshake}")

    if handshake.supports_extensions:
        extension_handshake = peer.send_extensions_handshake()
        peer.send_interested()
        peers_metadata_extension_id = extension_handshake.peers_metadata_extension_id

        metadata = peer.request_metadata(peers_metadata_extension_id)
        torrent_file = TorrentFile.from_metadata(magnet, metadata)

        content = download(torrent_file=torrent_file, piece_nr=piece_nr, peer=peer)
        save_file(destination, content)
