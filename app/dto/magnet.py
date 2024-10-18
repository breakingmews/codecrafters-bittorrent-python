import struct
from dataclasses import dataclass
from dataclasses import field

import bencodepy

from app.dto.peer_message import BitField


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
        extension_encoded = struct.pack("!I", extension_length) + struct.pack("!BB", self.id_,
                                                                              self.extension_message_id) + payload_encoded
        return extension_encoded

    @staticmethod
    def decode(buffer: bytes):
        bitfield = BitField.decode(buffer)
        ext_buffer = buffer[4 + bitfield.length:]
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


class Metadata(Extension):
    ...


class Request(Metadata):
    def __init__(self, peers_metadata_extension_id: int):
        self.payload = {'msg_type': 0, 'piece': 0}
        self.extension_message_id = peers_metadata_extension_id


class Response(Metadata):
    ...
