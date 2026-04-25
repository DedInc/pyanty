import json
import random

CPU_DISTRIBUTIONS = {
    "windows": {2: 5, 4: 35, 6: 25, 8: 20, 12: 10, 16: 4, 24: 1},
    "macos": {4: 15, 8: 50, 10: 20, 12: 10, 16: 4, 24: 1},
    "linux": {2: 10, 4: 40, 6: 20, 8: 15, 12: 10, 16: 4, 32: 1},
}
RAM_DISTRIBUTIONS = {
    "low_end": [4, 8],
    "mid_range": [8, 16],
    "high_end": [16, 32],
    "enthusiast": [32, 64],
}
PLATFORM_NAMES = {
    "windows": "Win32",
    "macos": "MacIntel",
    "linux": "Linux x86_64",
    "android": "Linux armv8l",
}
PLATFORM_VERSIONS = {
    "windows": "15.0.0",
    "macos": None,
    "linux": None,
    "android": None,
}


def join_filter_value(value: object) -> object:
    if isinstance(value, (list, tuple, set)):
        return ",".join(map(str, value))
    return value


def select_fingerprint(fingerprint: object) -> object:
    if fingerprint is None:
        return {}
    if isinstance(fingerprint, list):
        return random.choice(fingerprint) if fingerprint else {}
    return fingerprint


def is_bablosoft_fingerprint(fingerprint: object) -> bool:
    return isinstance(fingerprint, dict) and bool(fingerprint.get("found"))


def is_dolphin_fingerprint(fingerprint: object) -> bool:
    required = ("browser", "os", "webgl", "userAgent", "screen")
    return isinstance(fingerprint, dict) and all(key in fingerprint for key in required)


def is_kameleo_fingerprint(fingerprint: object) -> bool:
    required = ("id", "device", "os", "browser", "webglMeta", "userAgent")
    return isinstance(fingerprint, dict) and all(key in fingerprint for key in required)


def normalize_platform(platform: object) -> str:
    platform = str(platform or "").lower()
    if "win" in platform:
        return "windows"
    if "mac" in platform or "ios" in platform:
        return "macos"
    if "android" in platform:
        return "android"
    if "linux" in platform:
        return "linux"
    return "windows"


def platform_from_user_agent(user_agent: str) -> str:
    if "Macintosh" in user_agent or "Mac OS" in user_agent:
        return "macos"
    if "Linux" in user_agent:
        return "linux"
    return "windows"


def get_default_platform_name(platform: str) -> str:
    return PLATFORM_NAMES.get(platform, "Win32")


def get_default_platform_version(platform: str) -> str | None:
    return PLATFORM_VERSIONS.get(platform)


def get_default_cpu_architecture(platform: str) -> str:
    if platform == "android":
        return "arm"
    return "x86"


def loads_json_value(value: object, default: object = None) -> object:
    if value is None:
        return default
    if isinstance(value, (list, dict)):
        return value
    try:
        return json.loads(value)
    except (TypeError, json.JSONDecodeError):
        return default


def generate_realistic_cpu_cores(platform: str = "windows") -> int:
    platform_key = platform.lower()
    if platform_key not in CPU_DISTRIBUTIONS:
        platform_key = "windows"

    core_weights = CPU_DISTRIBUTIONS[platform_key]
    cores = list(core_weights.keys())
    weights = list(core_weights.values())
    return random.choices(cores, weights=weights)[0]


def generate_realistic_ram_gb(platform: str = "windows", cpu_cores: int = 8) -> int:
    tier, weights = _ram_tier(cpu_cores)
    ram_options = RAM_DISTRIBUTIONS[tier]

    if platform.lower() == "macos":
        if tier == "low_end":
            ram_options = [8, 16]
            weights = [50, 50]
        elif tier == "mid_range":
            ram_options = [16, 32]
            weights = [60, 40]

    return random.choices(ram_options, weights=weights)[0]


def get_realistic_hardware_specs(platform: str = "windows") -> dict[str, int]:
    cpu_cores = generate_realistic_cpu_cores(platform)
    ram_gb = generate_realistic_ram_gb(platform, cpu_cores)
    return {"cpu": cpu_cores, "ram": ram_gb}


def _ram_tier(cpu_cores: int) -> tuple[str, list[int]]:
    if cpu_cores <= 4:
        return "low_end", [30, 70]
    if cpu_cores <= 8:
        return "mid_range", [40, 60]
    if cpu_cores <= 16:
        return "high_end", [60, 40]
    return "enthusiast", [70, 30]
