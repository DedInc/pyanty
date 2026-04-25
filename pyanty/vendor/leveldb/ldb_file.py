"""Reader for LevelDB table files."""

import io
import os
import pathlib
import struct
import typing

from .. import ccl_simplesnappy
from .blocks import Block
from .models import BlockHandle, Record


class LdbFile:
    """A leveldb table (.ldb or .sst) file."""

    BLOCK_TRAILER_SIZE = 5
    FOOTER_SIZE = 48
    MAGIC = 0xDB4775248B80FB57

    def __init__(self, file: pathlib.Path):
        if not file.exists():
            raise FileNotFoundError(file)

        self.path = file
        self.file_no = int(file.stem, 16)

        self._f = file.open("rb")
        self._f.seek(-LdbFile.FOOTER_SIZE, os.SEEK_END)

        self._meta_index_handle = BlockHandle.from_stream(self._f)
        self._index_handle = BlockHandle.from_stream(self._f)
        self._f.seek(-8, os.SEEK_END)
        (magic,) = struct.unpack("<Q", self._f.read(8))
        if magic != LdbFile.MAGIC:
            raise ValueError(f"Invalid magic number in {file}")

        self._index = self._read_index()

    def _read_block(self, handle: BlockHandle) -> Block:
        # block is the size in the blockhandle plus the trailer
        # the trailer is 5 bytes long.
        # idx  size  meaning
        # 0    1     CompressionType (0 = none, 1 = snappy)
        # 1    4     CRC32

        self._f.seek(handle.offset)
        raw_block = self._f.read(handle.length)
        trailer = self._f.read(LdbFile.BLOCK_TRAILER_SIZE)

        if (
            len(raw_block) != handle.length
            or len(trailer) != LdbFile.BLOCK_TRAILER_SIZE
        ):
            raise ValueError(
                f"Could not read all of the block at offset {handle.offset} in file {self.path}"
            )

        is_compressed = trailer[0] != 0
        if is_compressed:
            with io.BytesIO(raw_block) as buff:
                raw_block = ccl_simplesnappy.decompress(buff)

        return Block(raw_block, is_compressed, self, handle.offset)

    def _read_index(self) -> tuple[tuple[bytes, BlockHandle], ...]:
        index_block = self._read_block(self._index_handle)
        # key is earliest key, value is BlockHandle to that data block
        return tuple(
            (entry.key, BlockHandle.from_bytes(entry.value)) for entry in index_block
        )

    def __iter__(self) -> typing.Iterable[Record]:
        """Iterate Records in this Table file"""
        for _block_key, handle in self._index:
            block = self._read_block(handle)
            for entry in block:
                yield Record.ldb_record(
                    entry.key,
                    entry.value,
                    self.path,
                    block.offset
                    if block.was_compressed
                    else block.offset + entry.block_offset,
                    block.was_compressed,
                )

    def close(self):
        self._f.close()
