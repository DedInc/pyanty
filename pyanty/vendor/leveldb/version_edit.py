"""LevelDB manifest version edit parsing."""

import dataclasses
import enum
import io
import typing
from collections import namedtuple

from .varint import read_le_varint, read_length_prefixed_blob


class VersionEditTag(enum.IntEnum):
    """
    See: https://github.com/google/leveldb/blob/master/db/version_edit.cc
    """

    Comparator = 1
    LogNumber = 2
    NextFileNumber = 3
    LastSequence = 4
    CompactPointer = 5
    DeletedFile = 6
    NewFile = 7
    # 8 was used for large value refs
    PrevLogNumber = 9


@dataclasses.dataclass(frozen=True)
class VersionEdit:
    """
    See:
    https://github.com/google/leveldb/blob/master/db/version_edit.h
    https://github.com/google/leveldb/blob/master/db/version_edit.cc
    """

    comparator: str = None
    log_number: int = None
    prev_log_number: int = None
    last_sequence: int = None
    next_file_number: int = None
    compaction_pointers: tuple[typing.Any] = tuple()
    deleted_files: tuple[typing.Any] = tuple()
    new_files: tuple[typing.Any] = tuple()

    @classmethod
    def from_buffer(cls, buffer: bytes):
        comparator = None
        log_number = None
        prev_log_number = None
        last_sequence = None
        next_file_number = None
        compaction_pointers = []
        deleted_files = []
        new_files = []

        compaction_pointer_nt = namedtuple("CompactionPointer", ["level", "pointer"])
        deleted_file_nt = namedtuple("DeletedFile", ["level", "file_no"])
        new_file_nt = namedtuple(
            "NewFile", ["level", "file_no", "file_size", "smallest_key", "largest_key"]
        )

        with io.BytesIO(buffer) as b:
            while b.tell() < len(buffer) - 1:
                tag = read_le_varint(b, is_google_32bit=True)

                if tag == VersionEditTag.Comparator:
                    comparator = read_length_prefixed_blob(b).decode("utf-8")
                elif tag == VersionEditTag.LogNumber:
                    log_number = read_le_varint(b)
                elif tag == VersionEditTag.PrevLogNumber:
                    prev_log_number = read_le_varint(b)
                elif tag == VersionEditTag.NextFileNumber:
                    next_file_number = read_le_varint(b)
                elif tag == VersionEditTag.LastSequence:
                    last_sequence = read_le_varint(b)
                elif tag == VersionEditTag.CompactPointer:
                    level = read_le_varint(b, is_google_32bit=True)
                    compaction_pointer = read_length_prefixed_blob(b)
                    compaction_pointers.append(
                        compaction_pointer_nt(level, compaction_pointer)
                    )
                elif tag == VersionEditTag.DeletedFile:
                    level = read_le_varint(b, is_google_32bit=True)
                    file_no = read_le_varint(b)
                    deleted_files.append(deleted_file_nt(level, file_no))
                elif tag == VersionEditTag.NewFile:
                    level = read_le_varint(b, is_google_32bit=True)
                    file_no = read_le_varint(b)
                    file_size = read_le_varint(b)
                    smallest = read_length_prefixed_blob(b)
                    largest = read_length_prefixed_blob(b)
                    new_files.append(
                        new_file_nt(level, file_no, file_size, smallest, largest)
                    )

        return cls(
            comparator,
            log_number,
            prev_log_number,
            last_sequence,
            next_file_number,
            tuple(compaction_pointers),
            tuple(deleted_files),
            tuple(new_files),
        )
