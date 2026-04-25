"""Small LevelDB record/value objects."""

import enum
import io
import os
import struct
import dataclasses
import typing

from .varint import read_le_varint


@dataclasses.dataclass
class BlockHandle:
    """See: https://github.com/google/leveldb/blob/master/doc/table_format.md
    A BlockHandle contains an offset and length of a block in an ldb table file"""

    offset: int
    length: int

    @classmethod
    def from_stream(cls, stream: typing.BinaryIO) -> "BlockHandle":
        return cls(read_le_varint(stream), read_le_varint(stream))

    @classmethod
    def from_bytes(cls, data: bytes) -> "BlockHandle":
        with io.BytesIO(data) as stream:
            return BlockHandle.from_stream(stream)


@dataclasses.dataclass
class RawBlockEntry:
    """Raw key, value for a record in a LDB file Block, along with the offset within the block from which it came from
    See: https://github.com/google/leveldb/blob/master/doc/table_format.md"""

    key: bytes
    value: bytes
    block_offset: int


class FileType(enum.Enum):
    Ldb = 1
    Log = 2


class KeyState(enum.Enum):
    Deleted = 0
    Live = 1
    Unknown = 2


@dataclasses.dataclass
class Record:
    """A record from leveldb; includes details of the origin file, state, etc."""

    key: bytes
    value: bytes
    seq: int
    state: KeyState
    file_type: FileType
    origin_file: os.PathLike
    offset: int
    was_compressed: bool

    @property
    def user_key(self) -> bytes:
        """Returns the "userkey" which omits the metadata bytes which may reside at the end of the raw key"""
        if self.file_type == FileType.Ldb:
            if len(self.key) < 8:
                return self.key
            else:
                return self.key[0:-8]
        else:
            return self.key

    @classmethod
    def ldb_record(
        cls,
        key: bytes,
        value: bytes,
        origin_file: os.PathLike,
        offset: int,
        was_compressed: bool,
    ) -> "Record":
        seq = (struct.unpack("<Q", key[-8:])[0]) >> 8
        if len(key) > 8:
            state = KeyState.Deleted if key[-8] == 0 else KeyState.Live
        else:
            state = KeyState.Unknown
        return cls(
            key, value, seq, state, FileType.Ldb, origin_file, offset, was_compressed
        )

    @classmethod
    def log_record(
        cls,
        key: bytes,
        value: bytes,
        seq: int,
        state: KeyState,
        origin_file: os.PathLike,
        offset: int,
    ) -> "Record":
        return cls(key, value, seq, state, FileType.Log, origin_file, offset, False)
