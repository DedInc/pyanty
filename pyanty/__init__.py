import sys

from .api import STABLE_CHROME_VERSION, DolphinAPI
from .api import client as _api_client
from .api import constants as _api_constants
from .api import releases as _releases
from .api import responses as _api_responses
from .browser import automation as _automation
from .browser import (
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
from .profiles import builder as _profile_builder
from .profiles import defaults as _profile_defaults
from .profiles import fingerprints as _fingerprint_utils
from .runtime import storage as _storage
from .vendor import ccl_leveldb as _ccl_leveldb
from .vendor import ccl_simplesnappy as _ccl_simplesnappy
from .vendor import leveldb as _leveldb
from .vendor import snappy as _snappy

__all__ = [
    "DolphinAPI",
    "STABLE_CHROME_VERSION",
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
    from .browser import authorize_in_window as authorize_in_window

    __all__.append("authorize_in_window")


def _alias_legacy_module(name: str, module: object) -> None:
    sys.modules.setdefault(f"{__name__}.{name}", module)
    setattr(sys.modules[__name__], name, module)


_LEGACY_MODULES = {
    "api_client": _api_client,
    "api_constants": _api_constants,
    "api_responses": _api_responses,
    "ccl_leveldb": _ccl_leveldb,
    "ccl_simplesnappy": _ccl_simplesnappy,
    "fingerprint_utils": _fingerprint_utils,
    "profile_builder": _profile_builder,
    "profile_defaults": _profile_defaults,
    "pyanty": _automation,
    "releases": _releases,
    "utils": _storage,
    "_leveldb": _leveldb,
    "_snappy": _snappy,
}

for _name, _module in _LEGACY_MODULES.items():
    _alias_legacy_module(_name, _module)

del _name, _module
