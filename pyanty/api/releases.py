import requests

from .constants import DOLPHIN_RELEASES_URL, DOLPHIN_RELEASES_URL_MIRROR

DEFAULT_DOLPHIN_RELEASE = "2026.112.222"


def get_latest_release() -> str:
    for url in (DOLPHIN_RELEASES_URL, DOLPHIN_RELEASES_URL_MIRROR):
        version = _fetch_release_version(url)
        if version:
            return version
    return DEFAULT_DOLPHIN_RELEASE


def _fetch_release_version(url: str) -> str | None:
    try:
        response = requests.get(url, timeout=5)
    except Exception:
        return None

    if response.status_code != 200:
        return None
    return _parse_release_version(response.text)


def _parse_release_version(content: str) -> str | None:
    for line in content.splitlines():
        if line.startswith("version:"):
            return line.split(":", 1)[1].strip()
    return None
