"""LevelDB table block iteration."""

import io
import struct
import typing

from .models import RawBlockEntry
from .varint import read_le_varint

if typing.TYPE_CHECKING:
    from .ldb_file import LdbFile


class Block:
    """Block from an .lldb (table) file. See: https://github.com/google/leveldb/blob/master/doc/table_format.md"""

    def __init__(
        self, raw: bytes, was_compressed: bool, origin: "LdbFile", offset: int
    ):
        self._raw = raw
        self.was_compressed = was_compressed
        self.origin = origin
        self.offset = offset

        (self._restart_array_count,) = struct.unpack("<I", self._raw[-4:])
        self._restart_array_offset = (
            len(self._raw) - (self._restart_array_count + 1) * 4
        )

    def get_restart_offset(self, index) -> int:
        offset = self._restart_array_offset + (index * 4)
        return struct.unpack("<i", self._raw[offset : offset + 4])[0]

    def get_first_entry_offset(self) -> int:
        return self.get_restart_offset(0)

    def __iter__(self) -> typing.Iterable[RawBlockEntry]:
        offset = self.get_first_entry_offset()
        with io.BytesIO(self._raw) as buff:
            buff.seek(offset)

            key = b""

            while buff.tell() < self._restart_array_offset:
                start_offset = buff.tell()
                shared_length = read_le_varint(buff, is_google_32bit=True)
                non_shared_length = read_le_varint(buff, is_google_32bit=True)
                value_length = read_le_varint(buff, is_google_32bit=True)

                # sense check
                if offset >= self._restart_array_offset:
                    raise ValueError(
                        "Reading start of entry past the start of restart array"
                    )
                if shared_length > len(key):
                    raise ValueError(
                        "Shared key length is larger than the previous key"
                    )

                key = key[:shared_length] + buff.read(non_shared_length)
                value = buff.read(value_length)

                yield RawBlockEntry(key, value, start_offset)
