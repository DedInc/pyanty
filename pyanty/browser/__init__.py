import sys

from .automation import (
    clean_trash,
    close_profile,
    download_driver_to_memory,
    get_browser,
    get_dolphin_driver,
    get_driver,
    run_profile,
    select_driver_executable,
    unpack_subarchives,
    unzip_driver_from_memory,
)

__all__ = [
    "clean_trash",
    "close_profile",
    "download_driver_to_memory",
    "get_browser",
    "get_dolphin_driver",
    "get_driver",
    "run_profile",
    "select_driver_executable",
    "unpack_subarchives",
    "unzip_driver_from_memory",
]

if sys.platform == "win32":
    from .automation import authorize_in_window as authorize_in_window

    __all__.append("authorize_in_window")
