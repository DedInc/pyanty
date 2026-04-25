"""Reader for LevelDB MANIFEST files."""

import pathlib
import re
import typing
from types import MappingProxyType

from .log_blocks import iter_log_batches, iter_raw_blocks
from .version_edit import VersionEdit


class ManifestFile:
    """
    Represents a manifest file which contains database metadata.

    Main use is to identify the level of files; use `file_to_level` to look up
    levels based on file number.
    """

    MANIFEST_FILENAME_PATTERN = "MANIFEST-([0-9A-F]{6})"

    def __init__(self, path: pathlib.Path):
        if match := re.match(ManifestFile.MANIFEST_FILENAME_PATTERN, path.name):
            self.file_no = int(match.group(1))
        else:
            raise ValueError("Invalid name for Manifest")

        self._f = path.open("rb")
        self.path = path
        levels = {}
        for edit in self:
            for new_file in edit.new_files:
                levels[new_file.file_no] = new_file.level
        self.file_to_level = MappingProxyType(levels)

    def _get_raw_blocks(self) -> typing.Iterable[bytes]:
        return iter_raw_blocks(self._f)

    def _get_batches(self) -> typing.Iterable[tuple[int, bytes]]:
        return iter_log_batches(self._f, self.path)

    def __iter__(self):
        for _batch_offset, batch in self._get_batches():
            yield VersionEdit.from_buffer(batch)

    def close(self):
        self._f.close()
