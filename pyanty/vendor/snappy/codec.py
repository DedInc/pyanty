"""Core Snappy block decompression."""

import enum
import io
import typing

from .streams import read_byte, read_le_varint, read_uint16, read_uint24, read_uint32


class ElementType(enum.IntEnum):
    """Run type in the compressed snappy data (literal data or offset to backreferenced data_"""

    Literal = 0
    CopyOneByte = 1
    CopyTwoByte = 2
    CopyFourByte = 3


def decompress(data: typing.BinaryIO) -> bytes:
    """Decompresses the snappy compressed data stream"""
    uncompressed_length = read_le_varint(data)
    # log(f"Uncompressed length: {uncompressed_length}")

    out = io.BytesIO()

    while True:
        # log(f"Reading tag at offset {start_offset}")
        type_byte = read_byte(data)
        if type_byte is None:
            break

        # log(f"Type Byte is {type_byte:02x}")

        tag = type_byte & 0x03

        # log(f"Element Type is: {ElementType(tag)}")

        if tag == ElementType.Literal:
            if ((type_byte & 0xFC) >> 2) < 60:  # embedded in tag
                length = 1 + ((type_byte & 0xFC) >> 2)
                # log(f"Literal length is embedded in type byte and is {length}")
            elif ((type_byte & 0xFC) >> 2) == 60:  # 8 bit
                length = 1 + read_byte(data)
                # log(f"Literal length is 8bit and is {length}")
            elif ((type_byte & 0xFC) >> 2) == 61:  # 16 bit
                length = 1 + read_uint16(data)
                # log(f"Literal length is 16bit and is {length}")
            elif ((type_byte & 0xFC) >> 2) == 62:  # 16 bit
                length = 1 + read_uint24(data)
                # log(f"Literal length is 24bit and is {length}")
            elif ((type_byte & 0xFC) >> 2) == 63:  # 16 bit
                length = 1 + read_uint32(data)
                # log(f"Literal length is 32bit and is {length}")
            else:
                raise ValueError()  # cannot ever happen

            literal_data = data.read(length)
            if len(literal_data) < length:
                raise ValueError("Couldn't read enough literal data")

            out.write(literal_data)

        else:
            if tag == ElementType.CopyOneByte:
                length = ((type_byte & 0x1C) >> 2) + 4
                offset = ((type_byte & 0xE0) << 3) | read_byte(data)
            elif tag == ElementType.CopyTwoByte:
                length = 1 + ((type_byte & 0xFC) >> 2)
                offset = read_uint16(data)
            elif tag == ElementType.CopyFourByte:
                length = 1 + ((type_byte & 0xFC) >> 2)
                offset = read_uint32(data)
            else:
                raise ValueError()  # cannot ever happen

            if offset == 0:
                raise ValueError("Offset cannot be 0")

            actual_offset = out.tell() - offset
            # log(f"Current Outstream Length: {out.tell()}")
            # log(f"Backreference length: {length}")
            # log(f"Backreference relative offset: {offset}")
            # log(f"Backreference absolute offset: {actual_offset}")

            # have to read incrementally because you might have to read data that you've just written
            # for i in range(length):
            #     out.write(out.getbuffer()[actual_offset + i: actual_offset + i + 1].tobytes())
            buffer = out.getbuffer()[actual_offset : actual_offset + length].tobytes()
            if offset - length <= 0:
                # better safe than sorry, this way we're sure to extend it
                # as much as needed without doing some extra calculations
                buffer = (buffer * length)[:length]
            out.write(buffer)

    result = out.getvalue()
    if uncompressed_length != len(result):
        raise ValueError("Wrong data length in uncompressed data")
        # TODO: allow a partial / potentially bad result via a flag in the function call?

    return result
