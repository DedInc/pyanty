"""
Compatibility facade for the bundled Snappy reader.

Copyright 2020, CCL Forensics

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

import sys
from pathlib import Path

from .snappy import (
    CRC_POLY,
    CRC_QUICK_TABLE,
    FRAME_MAGIC,
    ElementType,
    NoMoreData,
    check_masked_crc,
    crc32c,
    decompress,
    decompress_framed,
    make_crc_table,
    read_byte,
    read_frame,
    read_le_varint,
    read_uint16,
    read_uint24,
    read_uint32,
)

__version__ = "0.4"
__description__ = "Pure Python reimplementation of Google's Snappy decompression"
__contact__ = "Alex Caithness"
DEBUG = False

__all__ = [
    "CRC_POLY",
    "CRC_QUICK_TABLE",
    "DEBUG",
    "ElementType",
    "FRAME_MAGIC",
    "NoMoreData",
    "check_masked_crc",
    "crc32c",
    "decompress",
    "decompress_framed",
    "make_crc_table",
    "read_byte",
    "read_frame",
    "read_le_varint",
    "read_uint16",
    "read_uint24",
    "read_uint32",
]


def _main(in_path: str | Path, out_path: str | Path) -> None:
    in_path = Path(in_path)
    out_path = Path(out_path)
    with in_path.open("rb") as f:
        with out_path.open("wb") as out:
            decompress_framed(f, out)


if __name__ == "__main__":
    _main(sys.argv[1], sys.argv[2])
