import os
import sys
import shutil
import re
import json
import base64
import time
import requests

def get_profile_folder():
    if sys.platform == 'win32':
        return os.path.join(os.getenv('APPDATA'), 'dolphin_anty', 'browser_profiles')
    elif sys.platform == 'darwin':
        return os.path.expanduser('~/Library/Application Support/dolphin_anty/browser_profiles')
    else:
        return os.path.expanduser('~/.config/dolphin_anty/browser_profiles')


def clean_if_exists(dir_to_clean):
    if os.path.exists(dir_to_clean):
        try:
            shutil.rmtree(dir_to_clean)
        except OSError:
            pass


def collect_garbage(api=None, profile_id=None):
    profile_folder = get_profile_folder()

    if api is not None:
        api_profiles = []
        page = 1
        while True:
            profiles = api.get_profiles(page=page)['data']
            if not profiles:
                break
            api_profiles.extend(profiles)
            page += 1

        api_profile_ids = [f'{profile["id"]}' for profile in api_profiles]

        if not os.path.exists(profile_folder):
            return

        local_profile_ids = os.listdir(profile_folder)

        garbage_profile_ids = set(local_profile_ids) - set(api_profile_ids)

        for profile_id in garbage_profile_ids:
            profile_path = os.path.join(profile_folder, profile_id)
            clean_if_exists(profile_path)
    else:
        profile_path = os.path.join(profile_folder, f'{profile_id}')
        clean_if_exists(profile_path)


def scan_api_token():
    if sys.platform == 'win32':
        storage_path = os.path.join(os.getenv('APPDATA'), 'dolphin_anty', 'Local Storage', 'leveldb')
    elif sys.platform == 'darwin':
        storage_path = os.path.expanduser('~/Library/Application Support/dolphin_anty/Local Storage/leveldb')
    else:
        storage_path = os.path.expanduser('~/.config/dolphin_anty/Local Storage/leveldb')

    if not os.path.exists(storage_path) or not os.path.isdir(storage_path):
        raise ValueError(f'LevelDB storage path not found: {storage_path}')

    try:
        from .ccl_leveldb import RawLevelDb
        from pathlib import Path

        valid_tokens = []

        with RawLevelDb(Path(storage_path)) as db:
            for record in db.iterate_records_raw():
                try:
                    key = record.key.decode('utf-8', errors='ignore')
                    if 'accessToken' in key:
                        value = record.value.decode('utf-8', errors='ignore')
                        token = re.sub(r'[^A-Za-z0-9\.\-_]', '', value)

                        if is_valid_jwt_token(token):
                            valid_tokens.append(token)
                except Exception:
                    continue

        if valid_tokens:
            return valid_tokens[0]

        raise ValueError('No valid access token found in LevelDB database')

    except ImportError:
        raise ValueError('CCL LevelDB library not available. Please ensure ccl_leveldb module is properly installed.')
    except Exception as e:
        raise ValueError(f'Error reading LevelDB database: {str(e)}')


def is_valid_jwt_token(token):
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return False

        payload_b64 = parts[1]
        payload_b64 += '=' * (4 - len(payload_b64) % 4)

        try:
            payload_json = base64.b64decode(payload_b64).decode('utf-8')
            payload = json.loads(payload_json)
        except Exception:
            return False

        if 'exp' not in payload:
            return False
        current_time = time.time()
        exp_time = payload['exp']

        return exp_time > current_time

    except Exception:
        return False
