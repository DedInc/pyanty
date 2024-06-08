import requests
import re
import os
import sys
import chardet
from .utils import collect_garbage

data = requests.get('https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions.json').json()
STABLE_CHROME_VERSION = int(data['channels']['Stable']['version'].split('.')[0])
del data


class DolphinAPI:
    def __init__(self, api_key=None):
        if not api_key:
            api_key = self._scan_api_token()

        self.s = requests.Session()
        self.s.headers.update({
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'ru',
            'User-Agent': f'dolphin_anty_{self._get_latest_release()}_Windows_NT',
            'Referer': 'https://app.dolphin-anty-ru.online/',
            'Authorization': f'Bearer {api_key}'
        })
        self._collect_garbage()

    def get_profile(self, id):
        r = self.s.get(
            f'https://dolphin-anty-api.com/browser_profiles/{id}')
        try:
            return r.json()
        except:
            raise RuntimeError(r.text)

    def get_profiles(self, page=1, limit=50):
        r = self.s.get(
            f'https://dolphin-anty-api.com/browser_profiles?page={page}&limit={limit}')
        try:
            return r.json()
        except:
            raise RuntimeError(r.text)


    def get_extensions(self, page=1, limit=50):
        r = self.s.get(
            f'https://api.dolphin-anty-ru.online/extensions?page={page}&limit={limit}')
        try:
            return r.json()
        except:
            raise RuntimeError(r.text)

    def load_extension_from_url(self, url):
        r = self.s.post(
            f'https://api.dolphin-anty-ru.online/extensions', json={
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
                f'https://api.dolphin-anty-ru.online/extensions/upload-zipped',
                files=files,
                data=data
            )
        try:
            return r.json()
        except:
            raise RuntimeError(r.text)

    def delete_extensions(self, ids):
        r = self.s.delete(
            f'https://api.dolphin-anty-ru.online/extensions', json={
            "ids": ids
        })
        try:
            return r.json()
        except:
            raise RuntimeError(r.text)

    def create_profile(self, data):
        r = self.s.post(
            'https://dolphin-anty-api.com/browser_profiles', json=data)
        try:
            return r.json()
        except:
            raise RuntimeError(r.text)

    def edit_profile(self, id, data):
        r = self.s.patch(
            f'https://dolphin-anty-api.com/browser_profiles/{id}', json=data)
        try:
            return r.json()
        except:
            raise RuntimeError(r.text)

    def delete_profiles(self, ids):
        r = self.s.delete(
            'https://dolphin-anty-api.com/browser_profiles?forceDelete=1', json={'ids': ids})
        try:
            return r.json()
        except:
            raise RuntimeError(r.text)

    def generate_fingerprint(self, platform='windows', browser_version=STABLE_CHROME_VERSION - 1, screen='1920x1080'):
        r = self.s.get(
            f'https://dolphin-anty-api.com/fingerprints/fingerprint?platform={platform}&browser_type=anty&browser_version={browser_version}&type=fingerprint&screen={screen}')
        try:
            return r.json()
        except:
            raise RuntimeError(r.text)

    def check_proxy(self, **kwargs):
        r = self.s.post('http://localhost:3001/v1.0/check/proxy', json=kwargs)
        try:
            return r.json()
        except:
            raise RuntimeError(r.text)

    def generate_mac(self):
        r = self.s.get(
            'https://dolphin-anty-api.com/browser_profiles/generate-mac')
        try:
            return r.json()
        except:
            raise RuntimeError(r.text)

    def fingerprint_to_profile(self, name, tags=[], fingerprint={}):
        data = dict()
        data['name'] = name
        data['tags'] = tags

        data['platform'] = fingerprint['os']['name'].lower()
        data['browserType'] = 'anty'
        data['mainWebsite'] = 'none'

        data['useragent'] = {
            'mode': 'manual',
            'value': fingerprint['userAgent']
        }

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

        data['webglInfo'] = {
            'mode': 'manual',
            'vendor': fingerprint['webgl']['unmaskedVendor'],
            'renderer': fingerprint['webgl']['unmaskedRenderer'],
            'webgl2Maximum': fingerprint['webgl2Maximum']
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
            'resolution': None
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
        data['platformVersion'] = fingerprint['platformVersion']
        data['uaFullVersion'] = fingerprint['browser']['version']
        data['login'] = ''
        data['password'] = ''
        data['appCodeName'] = 'Mozilla'
        data['platformName'] = 'MacIntel'
        data['connectionDownlink'] = fingerprint['connection']['downlink']
        data['connectionEffectiveType'] = fingerprint['connection']['effectiveType']
        data['connectionRtt'] = fingerprint['connection']['rtt']
        data['connectionSaveData'] = fingerprint['connection']['saveData']
        data['cpuArchitecture'] = fingerprint['cpu']['architecture']
        data['osVersion'] = '10.15.7'
        data['vendorSub'] = ''
        data['productSub'] = fingerprint['productSub']
        data['vendor'] = fingerprint['vendor']
        data['product'] = fingerprint['product']

        return data

    def _get_latest_release(self):
        return requests.get('https://api.github.com/repos/dolphinrucom/anty-releases/releases/latest').json()['name']

    def _collect_garbage(self):
        collect_garbage(self)

    def _scan_api_token(self):
        if sys.platform == 'win32':
            storage_path = os.path.join(os.getenv('APPDATA'), 'dolphin_anty', 'Local Storage', 'leveldb')
        elif sys.platform == 'darwin':
            storage_path = os.path.expanduser('~/Library/Application Support/dolphin_anty/Local Storage/leveldb')
        else:
            storage_path = os.path.expanduser('~/.config/dolphin_anty/Local Storage/leveldb')

        if os.path.exists(storage_path):
            files = os.listdir(storage_path)
            for file in files:
                file = os.path.join(storage_path, file)
                try:
                    with open(file, 'rb') as f:
                        detector = chardet.UniversalDetector()
                        for chunk in iter(lambda: f.read(4096), b''):
                            detector.feed(chunk)
                            if detector.done:
                                break
                        detector.close()
                        encoding = detector.result['encoding']
                    with open(file, 'r', encoding=encoding) as f:
                        logs = f.read()
                    token_pattern = r'accessToken.*?(.{100,})"'
                    match = re.search(token_pattern, logs)
                    if match:
                        return match.group(1).split('')[2]
                except Exception as e:
                    print(e, file)
                    pass
        raise ValueError('Token Parse Exception')
