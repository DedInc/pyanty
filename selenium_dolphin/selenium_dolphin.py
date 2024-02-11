import requests
import os
import io
import zipfile
import platform
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


def run_profile(profile_id):
    return requests.get(f'http://localhost:3001/v1.0/browser_profiles/{profile_id}/start?automation=1').json()


def close_profile(profile_id):
    return requests.get(f'http://localhost:3001/v1.0/browser_profiles/{profile_id}/stop').json()


def download_driver(url, file_name):
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    block_size = 1024
    total_mb = total_size / (1024 * 1024)
    progress_bar = f"Downloading the Dolphin Anty driver... ["
    symbols_per_mb = 30 / total_mb
    downloaded_mb = 0
    with open(file_name, 'wb') as f:
        for data in response.iter_content(block_size):
            f.write(data)
            downloaded_mb += block_size / (1024 * 1024)
            progress = int(downloaded_mb * symbols_per_mb)
            progress_bar = f"Downloading the Dolphin Anty driver... [{progress}/{total_mb:.2f}MB [{'#' * progress}{'-' * (30 - progress)}]"
            print(f"\r{progress_bar}]", end="")
    print("]")


def select_supported_driver_archive(driver_archives, system=platform.system(), architecture=platform.machine()):
    for driver_archive in driver_archives:
        if system == 'Windows' and 'win' in driver_archive:
            if '64' in architecture and '64' in driver_archive:
                print(f"Selected {driver_archive}")
                return driver_archive
            elif '32' in driver_archive and '64' not in architecture:
                return driver_archive
        elif system == 'Darwin':
            if 'arm' in architecture and 'arm' in driver_archive:
                return driver_archive
            elif 'intel' in driver_archive:
                return driver_archive
        elif system == 'Linux' and 'linux' in driver_archive:
            return driver_archive

    raise ValueError("Unsupported combination of system and architecture")


def get_dolphin_driver():
    html = requests.get(
        'https://dolphin-anty.com/docs/basic-automation/#selenium').text
    driver_slices = html.split('/chromedriver')
    server_url = driver_slices[0].split('"')[-1]
    version = driver_slices[1].split('"')[0]
    archive_name = 'chromedriver' + version
    driver_url = server_url + '/' + archive_name

    if not os.path.exists(archive_name) and not os.path.exists('chromedriver'):
        download_driver(driver_url, archive_name)
        with zipfile.ZipFile(archive_name, 'r') as z:
            supported_driver_archive = select_supported_driver_archive(
                z.namelist())
            with z.open(supported_driver_archive) as z2:
                supported_driver_archive_bytes = io.BytesIO(z2.read())
                with zipfile.ZipFile(supported_driver_archive_bytes) as z3:
                    z3.extractall('chromedriver')

    files = os.listdir('chromedriver')
    if len(files) != 1:
        print('Executable selection may work incorrectly. See <https://github.com/DedInc/selenium_dolphin/pull/4>')
    executable_ext = '.exe' if platform.system() == 'Windows' else ''
    driver_path = os.path.join('chromedriver', "chromedriver" + executable_ext)
    return driver_path


def get_driver(options=Options(), driver_path='chromedriver.exe', port=9222):
    if not os.path.exists(driver_path):
        driver_path = get_dolphin_driver()
    options.add_experimental_option('debuggerAddress', f'127.0.0.1:{port}')
    driver = webdriver.Chrome(service=Service(driver_path), options=options)
    return driver
