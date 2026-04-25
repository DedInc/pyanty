"""Snappy framed stream decompression."""

import io
import struct
import typing

from .codec import decompress
from .crc import check_masked_crc
from .streams import NoMoreData

FRAME_MAGIC = bytes.fromhex("73 4E 61 50 70 59")


def read_frame(frame_stream: typing.BinaryIO):
    frame_header = frame_stream.read(4)
    if not frame_header:
        raise NoMoreData()
    if len(frame_header) < 4:
        raise ValueError("Could not read entire frame header")

    frame_id = frame_header[0]
    (frame_length,) = struct.unpack("<I", frame_header[1:] + b"\x00")

    data = frame_stream.read(frame_length)
    if len(data) != frame_length:
        raise ValueError(
            f"Could not read all data; wanted: {frame_length}; got: {len(data)}"
        )

    return frame_id, data


def decompress_framed(
    frame_stream: typing.BinaryIO, out_stream: typing.BinaryIO, *, mozilla_mode=False
):
    """
    Decompresses a Snappy framed format stream into another stream.

    :param frame_stream: Stream containing the Snappy Framed data
    :param out_stream: Stream that the decompressed data will be written to.
    :param mozilla_mode: If True, use the (non-standard) checksum format used by Mozilla
    :return:
    """
    header_type, header_raw = read_frame(frame_stream)
    if header_type != 0xFF or header_raw != FRAME_MAGIC:
        raise ValueError("Invalid magic")

    while True:
        frame_offset = frame_stream.tell()
        try:
            frame_type, frame_data = read_frame(frame_stream)
        except NoMoreData:
            break

        if frame_type == 0x00:  # compressed
            crc_raw = frame_data[0:4]
            with io.BytesIO(frame_data[4:]) as compressed:
                decompressed = decompress(compressed)
            (stored_crc,) = struct.unpack("<I", crc_raw)
            crc_match = check_masked_crc(
                stored_crc, decompressed, xor_value=0x0 if mozilla_mode else 0xFFFFFFFF
            )
            if not crc_match:
                raise ValueError(f"CRC mismatch in frame starting at {frame_offset}")

            out_stream.write(decompressed)
        elif frame_type == 0x01:  # decompressed
            crc_raw = frame_data[0:4]
            (stored_crc,) = struct.unpack("<I", crc_raw)
            crc_match = check_masked_crc(
                stored_crc,
                frame_data[4:],
                xor_value=0x0 if mozilla_mode else 0xFFFFFFFF,
            )
            if not crc_match:
                raise ValueError(f"CRC mismatch in frame starting at {frame_offset}")
            out_stream.write(frame_data[4:])
        elif frame_type == 0xFE:  # padding
            pass
        elif 0x02 <= frame_type <= 0x7F:  # reserved, unskippable
            raise ValueError("Reserved unskippable data")
        elif 0x80 <= frame_type <= 0xFE:  # reserved, skippable
            pass
        else:
            raise ValueError("unexpected frame")
