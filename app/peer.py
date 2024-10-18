import logging
import socket

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
        _log.debug(f"\nConnected to peer: {self.address}")

    def __del__(self):
        _log.debug("Destroying peer. Closing connection")
        self.socket.close()

    @staticmethod
    def _get_address(peer: str):
        address = peer.split(":")[0], int(peer.split(":")[1])
        _log.debug(f"Peer address: {address}")
        return address

    def send(self, buffer: bytes, size=1024) -> bytes:
        _log.debug(f"Sending: {buffer}")
        self.socket.sendall(buffer)
        return self.socket.recv(size)

    def wait(self, message_type: any, size=1024) -> bytes:
        _log.debug(f"\nWait for {message_type}")
        response = self.socket.recv(size)
        _log.debug(f"Received: {response}")
        is_keep_alive = PeerMessage.is_keep_alive(response)
        expected_message_type = (
            False
            if is_keep_alive
            else PeerMessage.decode(response).id_ == message_type.id_
        )
        wait_next = is_keep_alive or not expected_message_type
        if wait_next:
            self.wait(message_type, size)
        return response

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
        response = self.send(handshake.encode(), 68)
        _log.debug(f"\nHandshake response length: {len(response)}")
        _log.debug(f"Handshake response: {response}")

        decoded: Handshake = Handshake.decode(response[:68])
        _log.debug(f"Handshake decoded: {decoded}")
        _log.debug(f"\nPeer ID: {handshake.peer_id}")

        return decoded

    def send_extensions_handshake(self):
        handshake = ExtensionHandshake()
        response = self.send(handshake.encode())
        _log.debug(f"Extensions Handshake response: {response}")
        decoded: ExtensionHandshake = ExtensionHandshake.decode(response)
        return decoded

    def request_metadata(self, peers_metadata_extension_id: int):
        request = ExtensionRequest(peers_metadata_extension_id)
        response = self.send(request.encode())
        _log.debug(f"Metadata response: {response}")
        decoded: Data = Data.decode(response)
        return decoded

    def send_interested(self) -> Unchoke:
        _log.debug("\nSending Interested")
        interested = Interested().encode()
        response = self.send(interested)
        _log.debug(f"Received Unchoke: {response}")
        unchoke = Unchoke.decode(response)

        return unchoke

    def receive_bitfield(self):
        bitfield_bytes = self.wait(BitField)
        _log.debug(f"Received Bitfield: {bitfield_bytes}")
        bitfield: BitField = BitField.decode(bitfield_bytes)
        _log.debug(f"Received Bitfield: {bitfield}")
        return bitfield

    def request_piece(self, torrent_file: TorrentFile, piece_nr: int) -> bytes:
        _log.debug(f"Downloading piece {piece_nr}")
        blocks = []
        piece = b""
        for block in torrent_file.pieces[piece_nr].blocks:
            _log.debug(f"\n{block}")
            request = Request(piece_nr, block.offset, block.size)
            response = self.request_block(request)
            blocks.append(response)
            piece = b"".join(blocks)
            _log.debug(f"Piece size: {len(piece)}")

        _log.debug(f"\nReceived Piece {piece_nr}, size: {len(piece)}")
        return piece
