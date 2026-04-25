"""High-level LevelDB directory reader."""

import os
import pathlib
import re
import typing

from .ldb_file import LdbFile
from .log_file import LogFile
from .manifest import ManifestFile
from .models import Record


class RawLevelDb:
    DATA_FILE_PATTERN = r"[0-9]{6}\.(ldb|log|sst)"

    def __init__(self, in_dir: os.PathLike):
        self._in_dir = pathlib.Path(in_dir)
        if not self._in_dir.is_dir():
            raise ValueError("in_dir is not a directory")

        self._files = []
        latest_manifest = (0, None)
        for file in self._in_dir.iterdir():
            if self._is_data_file(file):
                self._files.append(self._open_data_file(file))
            if self._is_manifest_file(file):
                latest_manifest = self._latest_manifest(latest_manifest, file)

        self.manifest = self._open_manifest(latest_manifest[1])

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @property
    def in_dir_path(self) -> pathlib.Path:
        return self._in_dir

    def iterate_records_raw(self, *, reverse=False) -> typing.Iterable[Record]:
        files = sorted(self._files, reverse=reverse, key=lambda item: item.file_no)
        for file_containing_records in files:
            yield from file_containing_records

    def close(self):
        for file in self._files:
            file.close()
        if self.manifest:
            self.manifest.close()

    def _is_data_file(self, file: pathlib.Path) -> bool:
        return file.is_file() and re.match(RawLevelDb.DATA_FILE_PATTERN, file.name)

    def _is_manifest_file(self, file: pathlib.Path) -> bool:
        return file.is_file() and re.match(
            ManifestFile.MANIFEST_FILENAME_PATTERN, file.name
        )

    def _open_data_file(self, file: pathlib.Path):
        if file.suffix.lower() == ".log":
            return LogFile(file)
        return LdbFile(file)

    def _latest_manifest(
        self,
        current: tuple[int, pathlib.Path | None],
        file: pathlib.Path,
    ) -> tuple[int, pathlib.Path | None]:
        match = re.match(ManifestFile.MANIFEST_FILENAME_PATTERN, file.name)
        manifest_no = int(match.group(1), 16)
        if current[0] < manifest_no:
            return manifest_no, file
        return current

    def _open_manifest(self, file: pathlib.Path | None) -> ManifestFile | None:
        if file is None:
            return None
        return ManifestFile(file)
