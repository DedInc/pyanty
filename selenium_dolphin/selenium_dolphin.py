import requests
import os
import io
import zipfile
import shutil
import platform
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from pyppeteer import connect


def run_profile(profile_id, headless=False):
    is_headless_str = '' if not headless else '&headless=true'
    return requests.get(f'http://localhost:3001/v1.0/browser_profiles/{profile_id}/start?automation=1' + is_headless_str).json()


def close_profile(profile_id):
    return requests.get(f'http://localhost:3001/v1.0/browser_profiles/{profile_id}/stop').json()


def download_driver_to_memory(driver_url):
    response = requests.get(driver_url, stream=True)
    
    if response.status_code != 200 or 'zip' not in response.headers.get('Content-Type', ''):
        raise ValueError("The requested driver is not available.")

    total_size = int(response.headers.get('content-length', 0))
    block_size = 1024
    progress_bar_size = 30

    driver_content = io.BytesIO()
    downloaded_size = 0
    for data in response.iter_content(block_size):
        driver_content.write(data)
        downloaded_size += len(data)
        progress_fraction = downloaded_size / total_size
        progress_hash_count = int(progress_fraction * progress_bar_size)
        progress_bar = (
            f"Downloading the driver... [{progress_hash_count * '#'}{(progress_bar_size - progress_hash_count) * '-'}] "
            f"{downloaded_size / (1024 * 1024):.2f}/{total_size / (1024 * 1024):.2f}MB"
        )
        print(f"\r{progress_bar}", end="")
    
    driver_content.seek(0)
    print("\nDownload completed.")
    return driver_content

def get_dolphin_driver():
    docs_url = 'https://intercom.help/dolphinteam/en/articles/7127390-basic-automation-dolphin-anty'
    html = requests.get(docs_url).text
    driver_slices = html.split('/chromedriver')
    server_url = driver_slices[0].split('"')[-1]
    version = driver_slices[1].split('"')[0]
    archive_name = 'chromedriver' + version
    driver_url = server_url + '/' + archive_name
    return download_driver_to_memory(driver_url)


def unzip_driver_from_memory(driver_content):
    with zipfile.ZipFile(driver_content, 'r') as zip_ref:
        zip_ref.extractall(path=os.getcwd())

def clean_trash(zip_files):
    for zip_file in zip_files:
        os.remove(zip_file)

    if os.path.exists('__MACOSX'):
        shutil.rmtree(os.path.abspath('__MACOSX'))

def unpack_subarchives(system, architecture):
    zip_files = [f for f in os.listdir() if f.lower().endswith('.zip')]
    file_architecture = '64' if '64' in architecture else '86'

    for zip_file in zip_files:
        if system == 'Windows' and 'win' in zip_file.lower() and file_architecture in zip_file:
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                zip_ref.extractall(path=os.getcwd())
            break
        elif system == 'Linux' and 'linux' in zip_file.lower():
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                zip_ref.extractall(path=os.getcwd())
            break
        elif system == 'Darwin' and 'mac' in zip_file.lower():
            if 'arm' in architecture and 'arm' in zip_file:
                with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                    zip_ref.extractall(path=os.getcwd())
                break
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                zip_ref.extractall(path=os.getcwd())
            break
    clean_trash(zip_files)


def select_driver_executable(system, architecture):
    unpack_subarchives(system, architecture)
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
        driver_content = get_dolphin_driver()
        unzip_driver_from_memory(driver_content)
        driver_path = select_driver_executable(system, architecture)
   
    options.add_experimental_option('debuggerAddress', f'127.0.0.1:{port}')
    driver = webdriver.Chrome(service=Service(driver_path), options=options)
    return driver


async def get_browser(ws_endpoint, port):
    browser = await connect(browserWSEndpoint=f'ws://127.0.0.1:{port}{ws_endpoint}')
    pages = await browser.pages()
    page = pages[0]

    await page.bringToFront()
    return browser