from dataclasses import dataclass


@dataclass
class Magnet:
    info_hash: str
    filename: str
    tracker: str
