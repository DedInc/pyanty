"""LevelDB varint and length-prefixed blob readers."""

import typing


def _read_le_varint(
    stream: typing.BinaryIO, *, is_google_32bit=False
) -> tuple[int, bytes] | None:
    """Read varint from a stream.
    If the read is successful: returns a tuple of the (unsigned) value and the raw bytes making up that varint,
    otherwise returns None.
    Can be switched to limit the varint to 32 bit."""
    # this only outputs unsigned
    i = 0
    result = 0
    underlying_bytes = []
    limit = 5 if is_google_32bit else 10
    while i < limit:
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


def read_le_varint(stream: typing.BinaryIO, *, is_google_32bit=False) -> int | None:
    """Convenience version of _read_le_varint that only returns the value or None"""
    x = _read_le_varint(stream, is_google_32bit=is_google_32bit)
    if x is None:
        return None
    else:
        return x[0]


def read_length_prefixed_blob(stream: typing.BinaryIO) -> bytes:
    """Reads a blob of data which is prefixed with a varint length"""
    length = read_le_varint(stream)
    data = stream.read(length)
    if len(data) != length:
        raise ValueError(f"Could not read all data (expected {length}, got {len(data)}")
    return data
