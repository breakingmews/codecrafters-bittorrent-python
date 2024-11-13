import logging
import random
from typing import Optional, Tuple
from urllib.parse import parse_qs, urlparse

from app.bittorrent.peer import Peer
from app.bittorrent.tracker import Tracker
from app.dto.magnet import ExtensionHandshake, Magnet
from app.dto.peer_message import Handshake
from app.dto.torrent_file import TorrentFile

_log = logging.getLogger(__name__)


class TorrentClient:
    @staticmethod
    def save_file(destination: str, content: bytes) -> None:
        """
        Save the given content to the specified destination file.

        :param destination: The path to the file where the content will be saved.
        :param content: The content to be saved in the file.
        """
        try:
            with open(destination, "wb") as f:
                f.write(content)
            _log.info(f"Wrote file to {destination} - {len(content)} bytes")
        except IOError as e:
            _log.error(f"Failed to write file to {destination}: {e}")

    @staticmethod
    def download(
        torrent_file: TorrentFile,
        piece_nr: Optional[int] = None,
        peer: Optional[Peer] = None,
    ) -> bytes:
        """
        Download the specified piece or all pieces of the torrent file from a peer.
        """
        if not peer:
            _log.debug(f"{torrent_file}")
            peers = Tracker.get_peers(torrent_file)
            _log.debug(f"\nPeers:\n{'\n'.join(peers)}")

            if not peers:
                _log.error("No peers found")
                return b""

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
        Parse a magnet link and extract the info hash, filename, and tracker URL.

        :param link: The magnet link to be parsed.
        :return: A Magnet object containing the parsed info hash, filename, and tracker URL.

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
        """
        Initialize the MagnetClient with a magnet link.

        :param link: The magnet link to be parsed and used for initializing the client.
        """
        self.magnet = MagnetClient.parse_magnet_link(link)

        peers = Tracker.get_peers_from_magnet(self.magnet)
        self.peer = Peer(peers[random.randint(0, len(peers) - 1)])

    def do_handshake(self) -> Tuple[Handshake, ExtensionHandshake | None]:
        """
        Perform a handshake with the peer and receive the extension handshake if supported.

        :return: A tuple containing the Handshake and ExtensionHandshake (if any).
        """
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
        """
        Retrieve the torrent information by requesting metadata from the peer.

        :return: A TorrentFile object constructed from the retrieved metadata.
        """
        _, extension_handshake = self.do_handshake()
        peers_metadata_extension_id = extension_handshake.peers_metadata_extension_id  # type: ignore  # noqa
        metadata = self.peer.request_metadata(peers_metadata_extension_id)
        torrent_file = TorrentFile.from_metadata(self.magnet, metadata)

        return torrent_file

    def download(self, destination, piece_nr) -> None:
        """
        Download a specific piece or all pieces from the torrent and save to the destination.

        :param destination: The path where the downloaded content will be saved.
        :param piece_nr: The piece number to download. If None, all pieces are downloaded.
        """
        torrent_file = self.info()
        self.peer.send_interested()
        content = TorrentClient.download(
            torrent_file=torrent_file, piece_nr=piece_nr, peer=self.peer
        )
        TorrentClient.save_file(destination, content)
