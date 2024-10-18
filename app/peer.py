import socket
from typing import Tuple

from app.dto.peer_message import (
    BitField,
    Handshake,
    Interested,
    Request,
    Unchoke, PeerMessage,
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

    def wait(self, message_type: any, size=1024) -> bytes:
        print(f"Wait for {message_type}")

        response = self.socket.recv(size)
        print(f"Received: {response}")
        is_keep_alive = PeerMessage.is_keep_alive(response)
        expected_message_type = False if is_keep_alive else PeerMessage.decode(response).id_ == message_type.id_
        wait_next = is_keep_alive or not expected_message_type
        if wait_next:
            self.wait(message_type, size)
        return response

    def shake_hands(self, torrent_file: TorrentFile) -> Tuple[Handshake, BitField]:
        handshake = Handshake(torrent_file.sha1_info_hash)
        print(f"Handshake: {handshake}")
        response = self.send(handshake.encode())
        print(f"\nHandshake response length: {len(response)}")
        print(f"\nHandshake response: {response}")

        decoded: Handshake = Handshake.decode(response[:68])
        print(f"\nHandshake decoded: {decoded}")

        """
        if len(response) == 75:
            bitfield: BitField = BitField.decode(response[68:])
            if bitfield.id_ != BitField.id_:
                bitfield = BitField.decode(self.wait(BitField))
        else:
            bitfield = BitField.decode(self.wait(BitField))
        """
        bitfield: BitField = BitField.decode(response[68:])
        print(f"\nBitfield decoded: {bitfield}")

        return decoded, bitfield

    def interested(self) -> Unchoke:
        interested = Interested().encode()
        response = self.send(interested, 5)
        unchoke = Unchoke.decode(response)
        return unchoke

    def request_piece(self, torrent_file: TorrentFile, piece_nr: int) -> list:
        blocks = []
        for block in torrent_file.pieces[piece_nr].blocks:
            print(f"{block}")
            request = Request(block.ix, block.offset, block.size).encode()
            response = self.send(request)
            print(f"Response piece: {response}")
            blocks.append(response)

        return blocks
