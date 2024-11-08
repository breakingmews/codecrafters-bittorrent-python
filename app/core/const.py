import enum

PEER_ID = "00112233445566777777"


class Command(enum.Enum):
    DECODE = "decode"
    INFO = "info"
    PEERS = "peers"
    HANDSHAKE = "handshake"
    DOWNLOAD_PIECE = "download_piece"
    DOWNLOAD = "download"
    MAGNET_PARSE = "magnet_parse"
    MAGNET_HANDSHAKE = "magnet_handshake"
    MAGNET_INFO = "magnet_info"
    MAGNET_DOWNLOAD_PIECE = "magnet_download_piece"
    MAGNET_DOWNLOAD = "magnet_download"
