import struct
from dataclasses import dataclass, field

import bencodepy

from app.dto.peer_message import BitField, PeerMessage


@dataclass
class Magnet:
    info_hash: str
    filename: str
    tracker: str

    @property
    def sha1_info_hash(self) -> bytes:
        return bytes.fromhex(self.info_hash)


class Extension:
    length: int  # 4 bytes
    id_: int = 20  # 1 byte
    extension_message_id: int = 0  # 1 byte
    payload: dict = field(default_factory=dict)

    def encode(self) -> bytes:
        payload_encoded = bencodepy.encode(self.payload)
        extension_length = 1 + 1 + len(payload_encoded)
        extension_encoded = (
            struct.pack("!I", extension_length)
            + struct.pack("!BB", self.id_, self.extension_message_id)
            + payload_encoded
        )
        return extension_encoded

    @staticmethod
    def decode(buffer: bytes):
        ext_buffer = buffer
        if PeerMessage.is_bitfield(buffer):
            bitfield = BitField.decode(buffer)
            ext_buffer = buffer[4 + bitfield.length :]
        extension = Extension()
        extension.length = struct.unpack("!I", ext_buffer[:4])[0]
        extension.id_ = struct.unpack("!B", ext_buffer[4:5])[0]
        extension.extension_message_id = struct.unpack("!B", ext_buffer[5:6])[0]
        extension.payload = bencodepy.decode(ext_buffer[6:])
        return extension


@dataclass
class ExtensionHandshake(Extension):
    def __init__(self):
        self.payload = {"m": {"ut_metadata": 16}}

    @property
    def peers_metadata_extension_id(self):
        return self.payload[b"m"][b"ut_metadata"]


class Metadata(Extension): ...


class Request(Metadata):
    def __init__(self, peers_metadata_extension_id: int):
        self.payload = {"msg_type": 0, "piece": 0}
        self.extension_message_id = peers_metadata_extension_id


class Data(Metadata):
    @staticmethod
    def decode(buffer: bytes):
        ext_buffer = buffer
        if PeerMessage.is_bitfield(buffer):
            bitfield = BitField.decode(buffer)
            ext_buffer = buffer[4 + bitfield.length :]

        data = Data()
        data.length = struct.unpack("!I", ext_buffer[:4])[0]
        data.id_ = struct.unpack("!B", ext_buffer[4:5])[0]
        data.extension_message_id = struct.unpack("!B", ext_buffer[5:6])[0]

        splitted = ext_buffer[6:].split(b"eed")
        first: dict = bencodepy.decode(splitted[0] + b"ee")
        second: dict = bencodepy.decode(b"d" + splitted[1])
        data.payload = dict((*first.items(), *second.items()))
        return data
