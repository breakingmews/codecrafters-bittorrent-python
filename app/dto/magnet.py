from dataclasses import dataclass


@dataclass
class Magnet:
    info_hash: str
    filename: str
    tracker: str

    @property
    def sha1_info_hash(self) -> bytes:
        return bytes.fromhex(self.info_hash)
