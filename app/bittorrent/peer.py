import logging
import socket
import struct

from app.dto.magnet import Data, ExtensionHandshake
from app.dto.magnet import Request as ExtensionRequest
from app.dto.peer_message import (
    BitField,
    Handshake,
    Interested,
    PeerMessage,
    Piece,
    Request,
    Unchoke,
)
from app.dto.torrent_file import TorrentFile

_log = logging.getLogger(__name__)


class Peer:
    def __init__(self, peer: str):
        self.address = Peer._get_address(peer)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect(self.address)
        _log.debug(f"Connected to peer: {self.address}")

    def __del__(self):
        _log.debug("Destroying peer. Closing connection")
        self.socket.close()

    @staticmethod
    def _get_address(peer: str):
        address = peer.split(":")[0], int(peer.split(":")[1])
        _log.debug(f"Peer address: {address}")
        return address

    def send(self, buffer: bytes) -> None:
        _log.debug(f"Sending: {buffer}")
        self.socket.sendall(buffer)

    def receive(self):
        length_prefix = self.socket.recv(4)
        if PeerMessage.is_keep_alive(length_prefix):
            _log.debug("Received 'Keep alive'")
            return length_prefix
        length = struct.unpack("!I", length_prefix)[0]
        buffer = self.socket.recv(length)
        return length_prefix + buffer

    def request_block(self, request: Request) -> bytes:
        _log.debug(f"Request block: {request}")
        self.socket.sendall(request.encode())

        response = self.socket.recv(request.block_size)
        _log.debug(f"Chunk size: {len(response)}")
        if len(response) == 0:
            return b""
        piece = Piece.decode(response)
        block = piece.payload

        while True:
            response = self.socket.recv(request.block_size)
            _log.debug(f"Chunk size: {len(response)}")
            if PeerMessage.is_keep_alive(response):
                _log.debug(response)
                break

            block += response
            _log.debug(f"Block size: {len(block)}")

            if len(block) == request.block_size:
                break

        return block

    def shake_hands(self, sha1_info_hash: str, supports_extensions=False) -> Handshake:
        handshake = Handshake(
            sha1_info_hash=sha1_info_hash, supports_extensions=supports_extensions
        )
        _log.debug(f"Handshake: {handshake}")
        self.send(handshake.encode())
        response = self.socket.recv(68)
        _log.debug(f"Handshake response length: {len(response)}")
        _log.debug(f"Handshake response: {response}")

        decoded: Handshake = Handshake.decode(response)
        _log.debug(f"Handshake decoded: {decoded}")
        _log.debug(f"Peer ID: {handshake.peer_id}")

        return decoded

    def send_extensions_handshake(self):
        handshake = ExtensionHandshake().encode()
        _log.debug(f"Sending Extensions Handshake: {handshake}")
        self.send(handshake)
        response = self.receive()
        _log.debug(f"Extensions Handshake response: {response}")
        decoded: ExtensionHandshake = ExtensionHandshake.decode(response)
        return decoded

    def request_metadata(self, peers_metadata_extension_id: int):
        request = ExtensionRequest(peers_metadata_extension_id)
        self.send(request.encode())
        response = self.receive()
        _log.debug(f"Metadata response: {response}")
        decoded: Data = Data.decode(response)
        return decoded

    def send_interested(self) -> Unchoke:
        _log.debug("Sending Interested")
        interested = Interested().encode()
        self.send(interested)
        response = self.receive()
        _log.debug(f"Received Unchoke: {response}")
        unchoke = Unchoke.decode(response)

        return unchoke

    def receive_bitfield(self):
        bitfield_bytes = self.receive()
        _log.debug(f"Received Bitfield: {bitfield_bytes}")
        bitfield: BitField = BitField.decode(bitfield_bytes)
        _log.debug(f"Received Bitfield: {bitfield}")
        return bitfield

    def request_piece(self, torrent_file: TorrentFile, piece_nr: int) -> bytes:
        _log.debug(f"Downloading piece {piece_nr}")
        blocks = []
        piece = b""
        for block in torrent_file.pieces[piece_nr].blocks:
            _log.debug(f"{block}")
            request = Request(piece_nr, block.offset, block.size)
            response = self.request_block(request)
            blocks.append(response)
            piece = b"".join(blocks)
            _log.debug(f"Piece size: {len(piece)}")

        _log.debug(f"Received Piece {piece_nr}, size: {len(piece)}")
        return piece
