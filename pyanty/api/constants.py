import requests

DOLPHIN_API_BASE_URL = "https://dolphin-anty-api.com"
LOCAL_DOLPHIN_API_BASE_URL = "http://localhost:3001"
CHROME_VERSIONS_URL = (
    "https://googlechromelabs.github.io/chrome-for-testing/"
    "last-known-good-versions.json"
)
DOLPHIN_RELEASES_URL = "https://app.dolphin-anty-mirror3.com/anty-app/latest.yml"
DOLPHIN_RELEASES_URL_MIRROR = "https://app.dolphin-anty-mirror3.net/anty-app/latest.yml"
DOLPHIN_REFERER_URL = "https://app.dolphin-anty-ru.online/"
BABLOSOFT_FINGERPRINT_URL = "https://fingerprints.bablosoft.com/preview"
KAMELEO_API_BASE_URL = "http://localhost:5050"
JSONValue = dict[str, object] | list[object] | str | int | float | bool | None
DEFAULT_STABLE_CHROME_VERSION = 148


def fetch_stable_chrome_version(
    default: int = DEFAULT_STABLE_CHROME_VERSION,
) -> int:
    try:
        data = requests.get(CHROME_VERSIONS_URL, timeout=10).json()
        version = data["channels"]["Stable"]["version"]
        return int(version.split(".")[0])
    except (requests.RequestException, KeyError, TypeError, ValueError):
        return default


STABLE_CHROME_VERSION = fetch_stable_chrome_version()
