import requests
import random
from .utils import collect_garbage, scan_api_token

DOLPHIN_API_BASE_URL = "https://dolphin-anty-api.com"
LOCAL_DOLPHIN_API_BASE_URL = "http://localhost:3001"
CHROME_VERSIONS_URL = 'https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions.json'
GITHUB_RELEASES_URL = 'https://api.github.com/repos/dolphinrucom/anty-releases/releases/latest'
DOLPHIN_REFERER_URL = 'https://app.dolphin-anty-ru.online/'
BABLOSOFT_FINGERPRINT_URL = 'https://fingerprints.bablosoft.com/preview'

data = requests.get(CHROME_VERSIONS_URL).json()
STABLE_CHROME_VERSION = int(data['channels']['Stable']['version'].split('.')[0])
del data


class DolphinAPI:
    def __init__(self, api_key=None):
        if not api_key:
            api_key = scan_api_token()

        self.s = requests.Session()
        self.s.headers.update({
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'ru',
            'User-Agent': f'dolphin_anty_{self._get_latest_release()}_Windows_NT',
            'Referer': DOLPHIN_REFERER_URL,
            'Authorization': f'Bearer {api_key}'
        })
        collect_garbage()

    def get_profile(self, id):
        r = self.s.get(
            f'{DOLPHIN_API_BASE_URL}/browser_profiles/{id}')
        try:
            return r.json()
        except:
            raise RuntimeError(r.text)

    def get_profiles(self, page=1, limit=50):
        r = self.s.get(
            f'{DOLPHIN_API_BASE_URL}/browser_profiles?page={page}&limit={limit}')
        try:
            return r.json()
        except:
            raise RuntimeError(r.text)


    def get_extensions(self, page=1, limit=50):
        r = self.s.get(
            f'{DOLPHIN_API_BASE_URL}/extensions?page={page}&limit={limit}')
        try:
            return r.json()
        except:
            raise RuntimeError(r.text)

    def load_extension_from_url(self, url):
        r = self.s.post(
            f'{DOLPHIN_API_BASE_URL}/extensions', json={
            'url': url,
            'sharedToEntireTeam': False,
            'mainWebsite': ['all']
        })
        try:
            return r.json()
        except:
            raise RuntimeError(r.text)

    def load_extension_from_zip(self, extension_name, path):
        with open(path, 'rb') as file:
            files = {'file': ('a.zip', file, 'application/x-zip-compressed')}
            data = {
                'extensionName': extension_name,
                'sharedToEntireTeam': '0',
                'mainWebsite[]': 'all'
            }
            r = self.s.post(
                f'{DOLPHIN_API_BASE_URL}/extensions/upload-zipped',
                files=files,
                data=data
            )
        try:
            return r.json()
        except:
            raise RuntimeError(r.text)

    def delete_extensions(self, ids):
        r = self.s.delete(
            f'{DOLPHIN_API_BASE_URL}/extensions', json={
            "ids": ids
        })
        try:
            return r.json()
        except:
            raise RuntimeError(r.text)

    def create_profile(self, data):
        r = self.s.post(
            f'{DOLPHIN_API_BASE_URL}/browser_profiles', json=data)
        try:
            print(r.json())
            return r.json()
        except:
            raise RuntimeError(r.text)

    def edit_profile(self, id, data):
        r = self.s.patch(
            f'{DOLPHIN_API_BASE_URL}/browser_profiles/{id}', json=data)
        try:
            return r.json()
        except:
            raise RuntimeError(r.text)

    def delete_profiles(self, ids):
        r = self.s.delete(
            f'{DOLPHIN_API_BASE_URL}/browser_profiles?forceDelete=1', json={'ids': ids})
        try:
            return r.json()
        except:
            raise RuntimeError(r.text)

    def generate_fingerprint(self, platform='windows', browser_version=STABLE_CHROME_VERSION, screen='1920x1080'):
        r = self.s.get(
            f'{DOLPHIN_API_BASE_URL}/fingerprints/fingerprint?platform={platform}&browser_type=anty&browser_version={browser_version}&type=fingerprint&screen={screen}')
        try:
            return r.json()
        except:
            raise RuntimeError(r.text)

    def generate_fb_fingerprint(self, tags=['Desktop']):
        r = self.s.get(f'{BABLOSOFT_FINGERPRINT_URL}', params={'tags': ','.join(tags)})
        try:
            return r.json()
        except:
            raise RuntimeError(r.text)

    def check_proxy(self, **kwargs):
        r = self.s.post(f'{LOCAL_DOLPHIN_API_BASE_URL}/v1.0/check/proxy', json=kwargs)
        try:
            return r.json()
        except:
            raise RuntimeError(r.text)

    def generate_mac(self):
        r = self.s.get(
            f'{DOLPHIN_API_BASE_URL}/browser_profiles/generate-mac')
        try:
            return r.json()
        except:
            raise RuntimeError(r.text)

    def fingerprint_to_profile(self, name, tags=[], fingerprint={}):
        data = dict()
        data['name'] = name
        data['tags'] = tags
        data['browserType'] = 'anty'
        data['mainWebsite'] = 'none'

        data['deviceName'] = {
            'mode': 'off',
            'value': None
        }

        data['macAddress'] = {
            'mode': 'random',
            'value': None
        }

        data['webrtc'] = {
            'mode': 'altered',
            'ipAddress': None
        }

        data['canvas'] = {
            'mode': 'noise'
        }

        data['webgl'] = {
            'mode': 'noise'
        }

        data['webgpu'] = {
            'mode': 'manual'
        }

        data['clientRect'] = {
            'mode': 'noise'
        }

        data['timezone'] = {
            'mode': 'auto',
            'value': None
        }

        data['locale'] = {
            'mode': 'auto',
            'value': None
        }

        data['proxy'] = {}

        data['geolocation'] = {
            'mode': 'auto',
            'latitude': None,
            'longitude': None,
            'accuracy': None
        }


        data['audio'] = {
            'mode': 'real'
        }

        data['mediaDevices'] = {
            'mode': 'real',
            'audioInputs': None,
            'videoInputs': None,
            'audioOutputs': None
        }

        data['ports'] = {
            'mode': 'protect',
            'blacklist': '3389,5900,5800,7070,6568,5938'
        }

        data['doNotTrack'] = False
        data['args'] = []
        data['login'] = ''
        data['password'] = ''
        data['vendorSub'] = ''

        # Parse BABLOSOFT Fingerprint
        if 'found' in fingerprint and fingerprint.get('found'):
            ua = fingerprint.get('ua', '')
            platform_detected = 'windows'

            if 'Windows' in ua:
                platform_detected = 'windows'
                data['platform'] = 'windows'
                data['platformName'] = 'Win32'
            elif 'Macintosh' in ua or 'Mac OS' in ua:
                platform_detected = 'macos'
                data['platform'] = 'macos'
                data['platformName'] = 'MacIntel'
            elif 'Linux' in ua:
                platform_detected = 'linux'
                data['platform'] = 'linux'
                data['platformName'] = 'Linux x86_64'
            else:
                data['platform'] = 'windows'
                data['platformName'] = 'Win32'

            data['useragent'] = {
                'mode': 'manual',
                'value': fingerprint['ua']
            }

            data['webglInfo'] = {
                'mode': 'manual',
                'vendor': fingerprint.get('vendor', 'Google Inc. (AMD)'),
                'renderer': fingerprint.get('renderer', 'ANGLE (AMD, AMD Radeon (TM) R9 200 Series (0x00006811) Direct3D11 vs_5_0 ps_5_0, D3D11)'),
                'webgl2Maximum': {}
            }

            hardware_specs = self._get_realistic_hardware_specs(platform_detected)

            data['cpu'] = {
                'mode': 'manual',
                'value': hardware_specs['cpu']
            }

            data['memory'] = {
                'mode': 'manual',
                'value': hardware_specs['ram']
            }

            data['screen'] = {
                'mode': 'manual',
                'resolution': f'{fingerprint.get("width", 1920)}x{fingerprint.get("height", 1080)}'
            }

            if 'canvas' in fingerprint:
                data['canvas'] = {
                    'mode': 'manual',
                    'value': fingerprint['canvas']
                }
        elif 'browser' in fingerprint:
            data['platform'] = fingerprint['os']['name'].lower()

            data['useragent'] = {
                'mode': 'manual',
                'value': fingerprint['userAgent']
            }

            data['webglInfo'] = {
                'mode': 'manual',
                'vendor': fingerprint['webgl']['unmaskedVendor'],
                'renderer': fingerprint['webgl']['unmaskedRenderer'],
                'webgl2Maximum': fingerprint['webgl2Maximum']
            }

            data['cpu'] = {
                'mode': 'manual',
                'value': fingerprint['hardwareConcurrency']
            }

            data['memory'] = {
                'mode': 'manual',
                'value': fingerprint['deviceMemory']
            }

            data['screen'] = {
                'mode': 'real',
                'resolution': f'{fingerprint["screen"]["width"]}x{fingerprint["screen"]["height"]}'
            }

            data['platformVersion'] = fingerprint['platformVersion']
            data['uaFullVersion'] = fingerprint['browser']['version']
            data['appCodeName'] = fingerprint['appCodeName']
            data['platformName'] = fingerprint['platform']
            data['connectionDownlink'] = fingerprint['connection']['downlink']
            data['connectionEffectiveType'] = fingerprint['connection']['effectiveType']
            data['connectionRtt'] = fingerprint['connection']['rtt']
            data['connectionSaveData'] = fingerprint['connection']['saveData']
            data['cpuArchitecture'] = fingerprint['cpu']['architecture']
            data['osVersion'] = fingerprint['os']['version']
            data['productSub'] = fingerprint['productSub']
            data['vendor'] = fingerprint['vendor']
            data['product'] = fingerprint['product']
        else:
            raise ValueError('This type of fingerprint is not supported.')

        return data

    def _generate_realistic_cpu_cores(self, platform='windows'):
        cpu_distributions = {
            'windows': {
                2: 5,
                4: 35,
                6: 25,
                8: 20,
                12: 10,
                16: 4,
                24: 1
            },
            'macos': {
                4: 15,
                8: 50,
                10: 20,
                12: 10,
                16: 4,
                24: 1
            },
            'linux': {
                2: 10,
                4: 40,
                6: 20,
                8: 15,
                12: 10,
                16: 4,
                32: 1
            }
        }

        platform_key = platform.lower()
        if platform_key not in cpu_distributions:
            platform_key = 'windows'

        cores_weights = cpu_distributions[platform_key]
        cores = list(cores_weights.keys())
        weights = list(cores_weights.values())

        return random.choices(cores, weights=weights)[0]

    def _generate_realistic_ram_gb(self, platform='windows', cpu_cores=8):
        ram_distributions = {
            'low_end': [4, 8],
            'mid_range': [8, 16],
            'high_end': [16, 32],
            'enthusiast': [32, 64]
        }

        if cpu_cores <= 4:
            tier = 'low_end'
            weights = [30, 70]
        elif cpu_cores <= 8:
            tier = 'mid_range'
            weights = [40, 60]
        elif cpu_cores <= 16:
            tier = 'high_end'
            weights = [60, 40]
        else:
            tier = 'enthusiast'
            weights = [70, 30]

        if platform.lower() == 'macos':
            if tier == 'low_end':
                ram_options = [8, 16]
                weights = [50, 50]
            elif tier == 'mid_range':
                ram_options = [16, 32]
                weights = [60, 40]
        else:
            ram_options = ram_distributions[tier]

        return random.choices(ram_options, weights=weights)[0]

    def _get_realistic_hardware_specs(self, platform='windows'):
        cpu_cores = self._generate_realistic_cpu_cores(platform)
        ram_gb = self._generate_realistic_ram_gb(platform, cpu_cores)

        return {
            'cpu': cpu_cores,
            'ram': ram_gb
        }

    def _get_latest_release(self):
        return requests.get(GITHUB_RELEASES_URL).json()['name']
