import socket

from tqdm import tqdm

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
        print(f"\nWait for {message_type}")
        response = self.socket.recv(size)
        print(f"Received: {response}")
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
        print(f"Request block: {request}")
        self.socket.sendall(request.encode())

        response = self.socket.recv(request.block_size)
        print(f"Chunk size: {len(response)}")
        if len(response) == 0:
            return b""
        piece = Piece.decode(response)
        block = piece.payload

        while True:
            response = self.socket.recv(request.block_size)
            print(f"Chunk size: {len(response)}")
            if len(response) == 13:
                print(response)
            if PeerMessage.is_keep_alive(response):
                print(response)
                break

            block += response
            print(f"Block size: {len(block)}")

            if len(block) == request.block_size:
                break

        return block

    def shake_hands(self, torrent_file: TorrentFile) -> Handshake:
        handshake = Handshake(torrent_file.sha1_info_hash)
        print(f"Handshake: {handshake}")
        response = self.send(handshake.encode(), 68)
        print(f"\nHandshake response length: {len(response)}")
        print(f"Handshake response: {response}")

        decoded: Handshake = Handshake.decode(response[:68])
        print(f"Handshake decoded: {decoded}")
        print(f"\nPeer ID: {handshake.peer_id}")

        return decoded

    def send_interested(self) -> Unchoke:
        print("\nSending Interested")
        interested = Interested().encode()
        response = self.send(interested)
        print(f"Received Unchoke: {response}")
        unchoke = Unchoke.decode(response)

        return unchoke

    def receive_bitfield(self):
        bitfield_bytes = self.wait(BitField)
        bitfield: BitField = BitField.decode(bitfield_bytes)
        return bitfield

    def request_piece(self, torrent_file: TorrentFile, piece_nr: int) -> bytes:
        blocks = []
        piece = b""
        for block in tqdm(torrent_file.pieces[piece_nr].blocks):
            print(f"\n{block}")
            request = Request(piece_nr, block.offset, block.size)
            response = self.request_block(request)
            blocks.append(response)
            piece = b"".join(blocks)
            print(f"Piece size: {len(piece)}")

        print(f"\nReceived Piece {piece_nr}, size: {len(piece)}")
        return piece
