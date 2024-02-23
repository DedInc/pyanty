import requests
import os
import zipfile
import tarfile
import platform
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from pyppeteer import connect
from .api import STABLE_CHROME_VERSION


def run_profile(profile_id, headless=False):
    is_headless_str = '' if not headless else '&headless=true'
    return requests.get(f'http://localhost:3001/v1.0/browser_profiles/{profile_id}/start?automation=1' + is_headless_str).json()


def close_profile(profile_id):
    return requests.get(f'http://localhost:3001/v1.0/browser_profiles/{profile_id}/stop').json()


def download_driver(response, file_name, driver_version):
    total_size = int(response.headers.get('content-length', 0))
    block_size = 1024
    total_mb = total_size / (1024 * 1024)
    progress_bar = f"Downloading the Dolphin Anty driver v{driver_version}... ["
    symbols_per_mb = 30 / total_mb
    downloaded_mb = 0
    with open(file_name, 'wb') as f:
        for data in response.iter_content(block_size):
            f.write(data)
            downloaded_mb += block_size / (1024 * 1024)
            progress = int(downloaded_mb * symbols_per_mb)
            progress_bar = f"Downloading the Dolphin Anty driver v{driver_version}... [{progress}/{total_mb:.2f}MB [{'#' * progress}{'-' * (30 - progress)}]"
            print(f"\r{progress_bar}]", end="")
    print("]")


def get_dolphin_driver(driver_version):
    base_url = 'https://anty-assets.s3.eu-central-1.amazonaws.com/chromedriver'
    driver_path = 'chromedriver.zip'
    
    while driver_version > 0:
        archive_name = f'{base_url}{driver_version}.zip'
        try:
            response = requests.get(archive_name, stream=True)
            if response.status_code == 200 and 'zip' in response.headers.get('Content-Type', ''):
                download_driver(response, driver_path, driver_version)
                return driver_path
            else:
                print(f'Chromedriver version {driver_version} not found. Trying previous version.')
                driver_version -= 1
        except requests.RequestException as e:
            print(f'An error occurred: {e}')
            driver_version -= 1
    
    raise ValueError("Could not find a suitable chromedriver version.")


def unzip_driver(driver_path):
    if driver_path.endswith('.zip'):
        with zipfile.ZipFile(driver_path, 'r') as zip_ref:
            zip_ref.extractall(path=os.path.dirname(driver_path))
    elif driver_path.endswith('.tar.gz'):
        with tarfile.open(driver_path, 'r:gz') as tar_ref:
            tar_ref.extractall(path=os.path.dirname(driver_path))
    else:
        raise ValueError("Unsupported archive format")


def select_driver_executable(system, architecture):
    if system == 'Windows':
        executable_name = 'chromedriver.exe' if '64' in architecture else 'chromedriver_x86.exe'
    elif system == 'Darwin' or (system == 'Linux' and '64' in architecture):
        executable_name = 'chromedriver'
    else:
        raise ValueError("Unsupported operating system or architecture")
    
    if system != 'Windows':
        os.chmod(executable_name, 0o755)
    
    return executable_name


def get_driver(options=Options(), port=9222):
    system = platform.system()
    architecture = platform.machine()
    driver_path = select_driver_executable(system, architecture)

    if not os.path.exists(driver_path):
        driver_zip_path = get_dolphin_driver(STABLE_CHROME_VERSION)
        unzip_driver(driver_zip_path)
        os.remove(driver_zip_path)
   
    options.add_experimental_option('debuggerAddress', f'127.0.0.1:{port}')
    driver = webdriver.Chrome(service=Service(driver_path), options=options)
    return driver


async def get_browser(ws_endpoint, port):
    browser = await connect(browserWSEndpoint=f'ws://127.0.0.1:{port}{ws_endpoint}')
    pages = await browser.pages()
    page = pages[0]

    await page.bringToFront()
    return browser