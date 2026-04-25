"""Pure-Python Snappy decompression internals."""

from .codec import ElementType, decompress
from .crc import CRC_POLY, CRC_QUICK_TABLE, check_masked_crc, crc32c, make_crc_table
from .framed import FRAME_MAGIC, decompress_framed, read_frame
from .streams import (
    NoMoreData,
    read_byte,
    read_le_varint,
    read_uint16,
    read_uint24,
    read_uint32,
)

__all__ = [
    "CRC_POLY",
    "CRC_QUICK_TABLE",
    "ElementType",
    "FRAME_MAGIC",
    "NoMoreData",
    "check_masked_crc",
    "crc32c",
    "decompress",
    "decompress_framed",
    "make_crc_table",
    "read_byte",
    "read_frame",
    "read_le_varint",
    "read_uint16",
    "read_uint24",
    "read_uint32",
]
