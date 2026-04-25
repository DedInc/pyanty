import json

from .defaults import default_profile
from .fingerprints import (
    get_default_cpu_architecture,
    get_default_platform_name,
    get_default_platform_version,
    get_realistic_hardware_specs,
    is_bablosoft_fingerprint,
    is_dolphin_fingerprint,
    is_kameleo_fingerprint,
    loads_json_value,
    normalize_platform,
    platform_from_user_agent,
    select_fingerprint,
)


def fingerprint_to_profile(
    name: str,
    tags: list[str] | None = None,
    fingerprint: object = None,
) -> dict[str, object]:
    selected = select_fingerprint(fingerprint)
    data = default_profile(name, tags or [])

    if is_bablosoft_fingerprint(selected):
        return _apply_bablosoft_fingerprint(data, selected)
    if is_kameleo_fingerprint(selected):
        return _apply_kameleo_fingerprint(data, selected)
    if is_dolphin_fingerprint(selected):
        return _apply_dolphin_fingerprint(data, selected)

    raise ValueError("This type of fingerprint is not supported.")


def _apply_bablosoft_fingerprint(
    data: dict[str, object],
    fingerprint: dict[str, object],
) -> dict[str, object]:
    user_agent = str(fingerprint.get("ua", ""))
    platform = platform_from_user_agent(user_agent)
    hardware = get_realistic_hardware_specs(platform)

    data["platform"] = platform
    data["platformName"] = get_default_platform_name(platform)
    data["useragent"] = {"mode": "manual", "value": user_agent}
    data["webglInfo"] = {
        "mode": "manual",
        "vendor": fingerprint.get("vendor", "Google Inc. (AMD)"),
        "renderer": fingerprint.get(
            "renderer",
            "ANGLE (AMD, AMD Radeon (TM) R9 200 Series (0x00006811) "
            "Direct3D11 vs_5_0 ps_5_0, D3D11)",
        ),
        "webgl2Maximum": {},
    }
    data["cpu"] = {"mode": "manual", "value": hardware["cpu"]}
    data["memory"] = {"mode": "manual", "value": hardware["ram"]}
    data["screen"] = {
        "mode": "manual",
        "resolution": (
            f"{fingerprint.get('width', 1920)}x{fingerprint.get('height', 1080)}"
        ),
    }

    if "canvas" in fingerprint:
        data["canvas"] = {"mode": "manual", "value": fingerprint["canvas"]}
    return data


def _apply_kameleo_fingerprint(
    data: dict[str, object],
    fingerprint: dict[str, object],
) -> dict[str, object]:
    os_data = _as_dict(fingerprint.get("os"))
    browser_data = _as_dict(fingerprint.get("browser"))
    webgl_meta = _as_dict(fingerprint.get("webglMeta"))
    platform = normalize_platform(os_data.get("family"))
    hardware = get_realistic_hardware_specs(platform)

    data["platform"] = platform
    data["platformVersion"] = get_default_platform_version(platform)
    data["uaFullVersion"] = browser_data.get("version") or str(
        browser_data.get("major", "")
    )
    data["platformName"] = os_data.get("platform") or get_default_platform_name(
        platform
    )
    data["cpuArchitecture"] = get_default_cpu_architecture(platform)
    data["osVersion"] = os_data.get("version")
    data["productSub"] = "20030107"
    data["vendor"] = "Google Inc."
    data["product"] = "Gecko"
    data["appCodeName"] = "Mozilla"
    data["useragent"] = {"mode": "manual", "value": fingerprint.get("userAgent", "")}
    data["webglInfo"] = {
        "mode": "manual",
        "vendor": webgl_meta.get("vendor", "Google Inc."),
        "renderer": webgl_meta.get(
            "renderer",
            "ANGLE (Intel, Intel(R) HD Graphics Direct3D11 vs_5_0 ps_5_0)",
        ),
        "webgl2Maximum": "{}",
    }
    data["webgl2Maximum"] = {}
    data["cpu"] = {"mode": "manual", "value": hardware["cpu"]}
    data["memory"] = {"mode": "manual", "value": hardware["ram"]}
    data["screen"] = {"mode": "real", "resolution": None}
    data["fontsMode"] = "auto"
    return data


def _apply_dolphin_fingerprint(
    data: dict[str, object],
    fingerprint: dict[str, object],
) -> dict[str, object]:
    webgl2_maximum = loads_json_value(fingerprint.get("webgl2Maximum"), {})
    webgpu_value = fingerprint.get("webgpu")
    if webgpu_value is not None and not isinstance(webgpu_value, str):
        webgpu_value = json.dumps(webgpu_value)

    os_data = _as_dict(fingerprint["os"])
    webgl_data = _as_dict(fingerprint["webgl"])
    browser_data = _as_dict(fingerprint["browser"])
    connection = _as_dict(fingerprint["connection"])
    cpu_data = _as_dict(fingerprint["cpu"])
    screen = _as_dict(fingerprint["screen"])

    data["fingerprint"] = fingerprint
    data["platform"] = normalize_platform(os_data["name"])
    data["useragent"] = {"mode": "manual", "value": fingerprint["userAgent"]}
    data["webglInfo"] = {
        "mode": "manual",
        "vendor": webgl_data["unmaskedVendor"],
        "renderer": webgl_data["unmaskedRenderer"],
        "webgl2Maximum": fingerprint.get("webgl2Maximum", {}),
    }
    data["webgl2Maximum"] = webgl2_maximum
    if webgpu_value is not None:
        data["webgpu"] = {"mode": "manual", "value": webgpu_value}

    data["cpu"] = {"mode": "manual", "value": fingerprint["hardwareConcurrency"]}
    data["memory"] = {"mode": "manual", "value": fingerprint["deviceMemory"]}
    data["screen"] = {
        "mode": "real",
        "resolution": f"{screen['width']}x{screen['height']}",
    }
    data["platformVersion"] = fingerprint["platformVersion"]
    data["uaFullVersion"] = fingerprint.get("uaFullVersion", browser_data["version"])
    data["appCodeName"] = fingerprint["appCodeName"]
    data["platformName"] = fingerprint["platform"]
    data["connectionDownlink"] = connection["downlink"]
    data["connectionEffectiveType"] = connection["effectiveType"]
    data["connectionRtt"] = connection["rtt"]
    data["connectionSaveData"] = connection["saveData"]
    data["cpuArchitecture"] = cpu_data["architecture"]
    data["osVersion"] = os_data["version"]
    data["screenWidth"] = screen["width"]
    data["screenHeight"] = screen["height"]
    data["productSub"] = fingerprint["productSub"]
    data["vendor"] = fingerprint["vendor"]
    data["product"] = fingerprint["product"]
    _apply_dolphin_fonts(data, fingerprint)
    return data


def _apply_dolphin_fonts(
    data: dict[str, object],
    fingerprint: dict[str, object],
) -> None:
    fonts = loads_json_value(fingerprint.get("fonts"), [])
    if fonts:
        data["fontsMode"] = "manual"
        data["fonts"] = fonts
    else:
        data["fontsMode"] = "auto"


def _as_dict(value: object) -> dict[str, object]:
    if isinstance(value, dict):
        return value
    return {}
