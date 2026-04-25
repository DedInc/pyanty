"""Shared LevelDB log/manifest block parsing."""

import enum
import io
import struct
import typing

LOG_ENTRY_HEADER_SIZE = 7
LOG_BLOCK_SIZE = 32768


class LogEntryType(enum.IntEnum):
    Zero = 0
    Full = 1
    First = 2
    Middle = 3
    Last = 4


def iter_raw_blocks(
    file_obj: typing.BinaryIO,
    block_size: int = LOG_BLOCK_SIZE,
) -> typing.Iterable[bytes]:
    file_obj.seek(0)
    while chunk := file_obj.read(block_size):
        yield chunk


def iter_log_batches(
    file_obj: typing.BinaryIO,
    path: object,
    block_size: int = LOG_BLOCK_SIZE,
) -> typing.Iterable[tuple[int, bytes]]:
    in_record = False
    start_offset = 0
    block = b""

    for index, chunk in enumerate(iter_raw_blocks(file_obj, block_size)):
        with io.BytesIO(chunk) as buffer:
            while buffer.tell() < block_size - LOG_ENTRY_HEADER_SIZE + 1:
                header_offset = index * block_size + buffer.tell()
                header = buffer.read(LOG_ENTRY_HEADER_SIZE)
                if len(header) < LOG_ENTRY_HEADER_SIZE:
                    break

                _crc, length, raw_type = struct.unpack("<IHB", header)
                payload = buffer.read(length)
                payload_offset = header_offset + LOG_ENTRY_HEADER_SIZE
                block_type = LogEntryType(raw_type)

                if block_type == LogEntryType.Full:
                    if in_record:
                        raise ValueError(
                            "Full block whilst still building a block at offset "
                            f"{payload_offset} in {path}"
                        )
                    yield payload_offset, payload
                elif block_type == LogEntryType.First:
                    if in_record:
                        raise ValueError(
                            "First block whilst still building a block at offset "
                            f"{payload_offset} in {path}"
                        )
                    start_offset = payload_offset
                    block = payload
                    in_record = True
                elif block_type == LogEntryType.Middle:
                    if not in_record:
                        raise ValueError(
                            "Middle block whilst not building a block at offset "
                            f"{payload_offset} in {path}"
                        )
                    block += payload
                elif block_type == LogEntryType.Last:
                    if not in_record:
                        raise ValueError(
                            "Last block whilst not building a block at offset "
                            f"{payload_offset} in {path}"
                        )
                    block += payload
                    in_record = False
                    yield start_offset, block
                elif block_type != LogEntryType.Zero:
                    raise ValueError(f"Unsupported log block type {raw_type}")
