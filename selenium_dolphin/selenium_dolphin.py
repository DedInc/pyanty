import requests
import os
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

def get_dolphin_driver():
	html = requests.get('https://dolphin-anty.com/docs/basic-automation/#selenium').text
	driver_slices = html.split('/chromedriver')
	server_url = driver_slices[0].split('"')[-1]
	version = driver_slices[1].split('"')[0]
	file_name = 'chromedriver' + version
	driver_url = server_url + '/' + file_name

	if not os.path.exists(file_name) and not os.path.exists('chromedriver'):
	    download_driver(driver_url, file_name)
	    with zipfile.ZipFile(file_name, 'r') as z:
	        z.extractall('')

	if os.path.exists('chromedriver'):
		drivers = os.listdir('chromedriver')
		system = platform.system()
		architecture = platform.machine()
		for driver_file in drivers:			
			if system == 'Windows' and '.exe' in driver_file:
			    if '64' in architecture and '64' in driver_file:
			        break
			    elif '32' in driver_file and not '64' in architecture:
			    	break
			elif system == 'Darwin':
			    if 'arm' in architecture and 'arm' in driver_file:
			        break
			    elif 'intel' in driver_file:
			        break
			elif system == 'Linux' and 'linux' in driver_file:
			    break
		if not driver_file:
		    raise ValueError("Unsupported platform")

		driver_path = os.path.join(os.getcwd(), 'chromedriver', driver_file)
	return driver_path


def get_driver(options=Options(), driver_path='chromedriver.exe', port=9222):
	if not os.path.exists(driver_path):
		driver_path = get_dolphin_driver()
	options.add_experimental_option('debuggerAddress', f'127.0.0.1:{port}')
	driver = webdriver.Chrome(service=Service(driver_path), options=options)
	return driver