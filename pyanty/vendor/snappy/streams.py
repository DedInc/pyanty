"""Binary stream helpers used by the Snappy codec."""

import struct
import typing


class NoMoreData(Exception): ...


def _read_le_varint(stream: typing.BinaryIO) -> tuple[int, bytes] | None:
    """Read varint from a stream.
    If the read is successful: returns a tuple of the (unsigned) value and the raw bytes making up that varint,
    otherwise returns None"""
    # this only outputs unsigned
    i = 0
    result = 0
    underlying_bytes = []
    while i < 10:  # 64 bit max possible?
        raw = stream.read(1)
        if len(raw) < 1:
            return None
        (tmp,) = raw
        underlying_bytes.append(tmp)
        result |= (tmp & 0x7F) << (i * 7)
        if (tmp & 0x80) == 0:
            break
        i += 1
    return result, bytes(underlying_bytes)


def read_le_varint(stream: typing.BinaryIO) -> int | None:
    """Convenience version of _read_le_varint that only returns the value or None"""
    x = _read_le_varint(stream)
    if x is None:
        return None
    else:
        return x[0]


def read_uint16(stream: typing.BinaryIO) -> int:
    """Reads an Uint16 from stream"""
    return struct.unpack("<H", stream.read(2))[0]


def read_uint24(stream: typing.BinaryIO) -> int:
    """Reads an Uint24 from stream"""
    return struct.unpack("<I", stream.read(3) + b"\x00")[0]


def read_uint32(stream: typing.BinaryIO) -> int:
    """Reads an Uint32 from stream"""
    return struct.unpack("<I", stream.read(4))[0]


def read_byte(stream: typing.BinaryIO) -> int | None:
    """Reads a single byte from stream (or returns None if EOD is met)"""
    x = stream.read(1)
    if x:
        return x[0]

    return None
