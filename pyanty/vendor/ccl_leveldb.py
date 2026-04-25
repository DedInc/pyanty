"""
Compatibility facade for the bundled LevelDB reader.

Copyright 2020-2021, CCL Forensics

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from .leveldb import (
    Block,
    BlockHandle,
    FileType,
    KeyState,
    LdbFile,
    LogEntryType,
    LogFile,
    ManifestFile,
    RawBlockEntry,
    RawLevelDb,
    Record,
    VersionEdit,
    VersionEditTag,
    _read_le_varint,
    read_le_varint,
    read_length_prefixed_blob,
)

__version__ = "0.4"
__description__ = "A module for reading LevelDB databases"
__contact__ = "Alex Caithness"

__all__ = [
    "Block",
    "BlockHandle",
    "FileType",
    "KeyState",
    "LdbFile",
    "LogEntryType",
    "LogFile",
    "ManifestFile",
    "RawBlockEntry",
    "RawLevelDb",
    "Record",
    "VersionEdit",
    "VersionEditTag",
    "_read_le_varint",
    "read_le_varint",
    "read_length_prefixed_blob",
]
