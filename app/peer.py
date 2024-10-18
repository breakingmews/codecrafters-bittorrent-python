import socket
from typing import Tuple

from app.dto.peer_message import (
    BitField,
    Handshake,
    Interested,
    Piece,
    Request,
    Unchoke,
)
from app.dto.torrent_file import TorrentFile


class Peer:
    def __init__(self, peer: str):
        self.address = Peer._get_address(peer)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect(self.address)
        print(f"\nConnected to peer: {self.address}")

    @staticmethod
    def _get_address(peer: str):
        address = peer.split(":")[0], int(peer.split(":")[1])
        print(f"Peer address: {address}")
        return address

    def send(self, buffer: bytes, size=1024) -> bytes:
        print(f"Sending: {buffer}")
        self.socket.sendall(buffer)
        return self.socket.recv(size)

    def shake_hands(self, torrent_file: TorrentFile) -> Tuple[Handshake, BitField]:
        handshake = Handshake(torrent_file.sha1_info_hash)
        print(f"Handshake: {handshake}")
        response = self.send(handshake.encode(), 75)
        print(f"\nHandshake response length: {len(response)}")
        print(f"\nHandshake response: {response}")

        decoded: Handshake = Handshake.decode(response[:68])
        print(f"\nHandshake decoded: {decoded}")

        bitfield: BitField = BitField.decode(response[68:])
        print(f"\nBitfield decoded: {bitfield}")

        return decoded, bitfield

    def interested(self) -> Unchoke:
        interested = Interested().encode()
        response = self.send(interested, 5)
        unchoke = Unchoke.decode(response)
        return unchoke

    def request_piece(self, torrent_file: TorrentFile, piece_nr: int) -> Piece:
        request = Request(0, 0, torrent_file.length).encode()
        response = self.send(request, torrent_file.length)
        print(f"Response piece: {response}")
        piece = Piece.decode(response)
        return piece
