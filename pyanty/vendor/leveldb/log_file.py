"""Reader for LevelDB write-ahead log files."""

import io
import pathlib
import struct
import typing

from .log_blocks import (
    LOG_BLOCK_SIZE,
    LOG_ENTRY_HEADER_SIZE,
    iter_log_batches,
    iter_raw_blocks,
)
from .models import KeyState, Record
from .varint import read_le_varint


class LogFile:
    """A levelDb log (.log) file"""

    LOG_ENTRY_HEADER_SIZE = LOG_ENTRY_HEADER_SIZE
    LOG_BLOCK_SIZE = LOG_BLOCK_SIZE

    def __init__(self, file: pathlib.Path):
        if not file.exists():
            raise FileNotFoundError(file)

        self.path = file
        self.file_no = int(file.stem, 16)
        self._f = file.open("rb")

    def _get_raw_blocks(self) -> typing.Iterable[bytes]:
        return iter_raw_blocks(self._f)

    def _get_batches(self) -> typing.Iterable[tuple[int, bytes]]:
        return iter_log_batches(self._f, self.path)

    def __iter__(self) -> typing.Iterable[Record]:
        """Iterate Records in this Log file"""
        for batch_offset, batch in self._get_batches():
            with io.BytesIO(batch) as buff:
                header = buff.read(12)
                seq, count = struct.unpack("<QI", header)

                for index in range(count):
                    start_offset = batch_offset + buff.tell()
                    state = KeyState(buff.read(1)[0])
                    key_length = read_le_varint(buff, is_google_32bit=True)
                    key = buff.read(key_length)
                    if state != KeyState.Deleted:
                        value_length = read_le_varint(buff, is_google_32bit=True)
                        value = buff.read(value_length)
                    else:
                        value = b""

                    yield Record.log_record(
                        key, value, seq + index, state, self.path, start_offset
                    )

    def close(self):
        self._f.close()
