import random

import requests

from ..profiles.builder import fingerprint_to_profile
from ..profiles.fingerprints import (
    generate_realistic_cpu_cores,
    generate_realistic_ram_gb,
    get_default_cpu_architecture,
    get_default_platform_name,
    get_default_platform_version,
    get_realistic_hardware_specs,
    is_dolphin_fingerprint,
    is_kameleo_fingerprint,
    join_filter_value,
    loads_json_value,
    normalize_platform,
)
from ..runtime import collect_garbage, scan_api_token
from .constants import (
    BABLOSOFT_FINGERPRINT_URL,
    DOLPHIN_API_BASE_URL,
    DOLPHIN_REFERER_URL,
    KAMELEO_API_BASE_URL,
    LOCAL_DOLPHIN_API_BASE_URL,
    STABLE_CHROME_VERSION,
    JSONValue,
)
from .releases import get_latest_release
from .responses import parse_json_response


class DolphinAPI:
    def __init__(
        self,
        api_key: str | None = None,
        session: requests.Session | None = None,
    ) -> None:
        if not api_key:
            api_key = scan_api_token()

        self.s = session or requests.Session()
        self.s.headers.update(self._build_headers(api_key))
        collect_garbage()

    def get_profile(self, id: int | str) -> JSONValue:
        return self._request("GET", f"{DOLPHIN_API_BASE_URL}/browser_profiles/{id}")

    def get_profiles(self, page: int = 1, limit: int = 50) -> JSONValue:
        return self._request(
            "GET",
            f"{DOLPHIN_API_BASE_URL}/browser_profiles",
            params={"page": page, "limit": limit},
        )

    def get_extensions(self, page: int = 1, limit: int = 50) -> JSONValue:
        return self._request(
            "GET",
            f"{DOLPHIN_API_BASE_URL}/extensions",
            params={"page": page, "limit": limit},
        )

    def load_extension_from_url(self, url: str) -> JSONValue:
        payload = {"url": url, "sharedToEntireTeam": False, "mainWebsite": ["all"]}
        return self._request("POST", f"{DOLPHIN_API_BASE_URL}/extensions", json=payload)

    def load_extension_from_zip(self, extension_name: str, path: str) -> JSONValue:
        data = {
            "extensionName": extension_name,
            "sharedToEntireTeam": "0",
            "mainWebsite[]": "all",
        }
        with open(path, "rb") as file:
            files = {"file": ("a.zip", file, "application/x-zip-compressed")}
            return self._request(
                "POST",
                f"{DOLPHIN_API_BASE_URL}/extensions/upload-zipped",
                files=files,
                data=data,
            )

    def delete_extensions(self, ids: list[int | str]) -> JSONValue:
        return self._request(
            "DELETE", f"{DOLPHIN_API_BASE_URL}/extensions", json={"ids": ids}
        )

    def create_profile(self, data: dict[str, object]) -> JSONValue:
        return self._request(
            "POST", f"{DOLPHIN_API_BASE_URL}/browser_profiles", json=data
        )

    def edit_profile(self, id: int | str, data: dict[str, object]) -> JSONValue:
        return self._request(
            "PATCH", f"{DOLPHIN_API_BASE_URL}/browser_profiles/{id}", json=data
        )

    def delete_profiles(self, ids: list[int | str]) -> JSONValue:
        return self._request(
            "DELETE",
            f"{DOLPHIN_API_BASE_URL}/browser_profiles",
            params={"forceDelete": 1},
            json={"ids": ids},
        )

    def generate_fingerprint(
        self,
        platform: str = "windows",
        browser_version: int = STABLE_CHROME_VERSION,
        screen: str = "1920x1080",
    ) -> JSONValue:
        params = {
            "platform": platform,
            "browser_type": "anty",
            "browser_version": browser_version,
            "type": "fingerprint",
            "screen": screen,
        }
        return self._request(
            "GET", f"{DOLPHIN_API_BASE_URL}/fingerprints/fingerprint", params=params
        )

    def generate_fb_fingerprint(self, tags: list[str] | None = None) -> JSONValue:
        tags = tags or ["Desktop"]
        return self._request(
            "GET", BABLOSOFT_FINGERPRINT_URL, params={"tags": ",".join(tags)}
        )

    def generate_kameleo_fingerprint(
        self,
        deviceType: object = "desktop",
        osFamily: object = "windows",
        browserProduct: object = "chrome",
        browserVersion: str | None = None,
        random_fingerprint: bool = True,
        base_url: str = KAMELEO_API_BASE_URL,
    ) -> JSONValue:
        params = {
            "deviceType": join_filter_value(deviceType),
            "osFamily": join_filter_value(osFamily),
            "browserProduct": join_filter_value(browserProduct),
        }
        if browserVersion is not None:
            params["browserVersion"] = browserVersion

        response = requests.get(f"{base_url.rstrip('/')}/fingerprints", params=params)
        fingerprints = parse_json_response(response)
        if random_fingerprint and isinstance(fingerprints, list):
            return random.choice(fingerprints) if fingerprints else {}
        return fingerprints

    def check_proxy(self, **kwargs: object) -> JSONValue:
        return self._request(
            "POST", f"{LOCAL_DOLPHIN_API_BASE_URL}/v1.0/check/proxy", json=kwargs
        )

    def generate_mac(self) -> JSONValue:
        return self._request(
            "GET", f"{DOLPHIN_API_BASE_URL}/browser_profiles/generate-mac"
        )

    def fingerprint_to_profile(
        self,
        name: str,
        tags: list[str] | None = None,
        fingerprint: object = None,
    ) -> dict[str, object]:
        return fingerprint_to_profile(name, tags, fingerprint)

    def _request(self, method: str, url: str, **kwargs: object) -> JSONValue:
        response = self.s.request(method, url, **kwargs)
        return parse_json_response(response)

    def _build_headers(self, api_key: str) -> dict[str, str]:
        return {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "ru",
            "User-Agent": f"dolphin_anty_{self._get_latest_release()}_Windows_NT",
            "Referer": DOLPHIN_REFERER_URL,
            "Authorization": f"Bearer {api_key}",
        }

    def _join_filter_value(self, value: object) -> object:
        return join_filter_value(value)

    def _is_dolphin_fingerprint(self, fingerprint: dict[str, object]) -> bool:
        return is_dolphin_fingerprint(fingerprint)

    def _is_kameleo_fingerprint(self, fingerprint: dict[str, object]) -> bool:
        return is_kameleo_fingerprint(fingerprint)

    def _normalize_platform(self, platform: object) -> str:
        return normalize_platform(platform)

    def _get_default_platform_name(self, platform: str) -> str:
        return get_default_platform_name(platform)

    def _get_default_platform_version(self, platform: str) -> str | None:
        return get_default_platform_version(platform)

    def _get_default_cpu_architecture(self, platform: str) -> str:
        return get_default_cpu_architecture(platform)

    def _loads_json_value(self, value: object, default: object = None) -> object:
        return loads_json_value(value, default)

    def _generate_realistic_cpu_cores(self, platform: str = "windows") -> int:
        return generate_realistic_cpu_cores(platform)

    def _generate_realistic_ram_gb(
        self, platform: str = "windows", cpu_cores: int = 8
    ) -> int:
        return generate_realistic_ram_gb(platform, cpu_cores)

    def _get_realistic_hardware_specs(
        self, platform: str = "windows"
    ) -> dict[str, int]:
        return get_realistic_hardware_specs(platform)

    def _get_latest_release(self) -> str:
        return get_latest_release()
