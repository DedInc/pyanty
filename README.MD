# pyanty

A Python client for the Dolphin Anty API. It handles browser profile management and establishes remote debugging connections so you can attach Selenium, Playwright, Patchright, or Pyppeteer to Dolphin profiles.

Note: The Dolphin Anty desktop application **must be running locally** for the automation features (browser launching, port binding) to work. The local app exposes an API on port 3001 which this library hooks into.

## Installation

Install via pip. By default, it installs dependencies for Selenium.

```bash
pip install pyanty
```

If you plan to use other automation engines, install the respective extras:

```bash
pip install pyanty[playwright]
pip install pyanty[patchright]
pip install pyanty[pyppeteer]
pip install pyanty[all]
```

## Authentication

You can pass your API key explicitly when initializing the client. If you omit the API key, `pyanty` will try to scrape your current session token directly from Dolphin's local LevelDB storage. This only works if you are logged into the desktop app on the same machine.

```python
from pyanty import DolphinAPI

# Auto-fetches token from LevelDB (Windows/macOS/Linux)
api = DolphinAPI()

# Or pass it explicitly
api = DolphinAPI(api_key="your_api_token")
```

## Usage Examples

### 1. Managing profiles and attaching Selenium

This creates a profile with a random Windows fingerprint, launches it, and attaches a Selenium webdriver.

```python
import pyanty as dolphin
from pyanty import DolphinAPI, STABLE_CHROME_VERSION

api = DolphinAPI()

# Generate a basic Windows fingerprint
fingerprint = api.generate_fingerprint(
    platform='windows', 
    browser_version=STABLE_CHROME_VERSION
)

profile_data = api.fingerprint_to_profile(name='selenium_test', fingerprint=fingerprint)
profile_id = api.create_profile(profile_data)['browserProfileId']

# Start the profile via the local Dolphin app
response = dolphin.run_profile(profile_id)
port = response['automation']['port']

# Attach Selenium
driver = dolphin.get_driver(port=port)
driver.get('https://example.com/')
print(driver.title)
driver.quit()

# Clean up
dolphin.close_profile(profile_id)
api.delete_profiles([profile_id])
```

### 2. Playwright / Patchright

```python
import asyncio
import pyanty as dolphin
from pyanty import DolphinAPI, STABLE_CHROME_VERSION

api = DolphinAPI()
fingerprint = api.generate_fingerprint(platform='windows', browser_version=STABLE_CHROME_VERSION)
profile_data = api.fingerprint_to_profile(name='playwright_test', fingerprint=fingerprint)
profile_id = api.create_profile(profile_data)['browserProfileId']

run_info = dolphin.run_profile(profile_id)
port = run_info['automation']['port']
ws_endpoint = run_info['automation']['wsEndpoint']

async def main():
    # Use core='patchright' if you need the undetectable version
    browser = await dolphin.get_browser(ws_endpoint, port, core='playwright')
    pages = await browser.pages()
    page = pages[0]
    
    await page.goto('https://example.com/')
    await browser.disconnect()

asyncio.run(main())

dolphin.close_profile(profile_id)
api.delete_profiles([profile_id])
```

## Fingerprints

By default, Dolphin provides its own fingerprints. The library also includes parsers and generators for Bablosoft and Kameleo formats if you need different distribution curves.

### Bablosoft Fingerprints

```python
fingerprint =[]
while not 'ua' in fingerprint:
    # Tags can be: 'Desktop', 'Mobile', 'Microsoft Windows', 'Apple Mac', 'Android', 'Linux', 'Chrome', 'Safari', etc.
    fingerprint = api.generate_fb_fingerprint(tags=['Desktop', 'Microsoft Windows', 'Chrome'])

data = api.fingerprint_to_profile(name='bablosoft_profile', fingerprint=fingerprint)
profile_id = api.create_profile(data)['browserProfileId']
```

## Profile Customization

You can mutate the dictionary returned by `fingerprint_to_profile` before creating or editing the profile. 

```python
data = api.fingerprint_to_profile(name='custom_profile', fingerprint=fingerprint)

# Proxies
data['proxy'] = {
  'name': 'http://127.0.0.1:8080',
  'host': '127.0.0.1',
  'port': '8080',
  'type': 'http',
  'login': 'user',
  'password': 'password'
}

# Geolocation overrides
data['geolocation'] = {
  'mode': 'manual',
  'latitude': 52.5200,
  'longitude': 13.4050,
  'accuracy': 100
}

api.create_profile(data)
```

## Extensions

The API allows installing extensions globally so they are available when profiles launch.

```python
# From Chrome Web Store URL
api.load_extension_from_url('https://chromewebstore.google.com/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm')

# From a local zip archive
api.load_extension_from_zip(extension_name='MyExtension', path='./build/extension.zip')

# List and delete
exts = api.get_extensions()
api.delete_extensions([ext['id'] for ext in exts['data']])
```

## Quirks and Limitations

* **Garbage Collection:** When calling `dolphin.close_profile(profile_id)`, the module triggers a local directory cleanup in the Dolphin app data folder. Be aware of this if you rely on maintaining local state outside of standard browser persistence.
* **Driver Download:** If `get_driver()` doesn't find the correct Chromedriver for your OS, it will try to download it straight into memory from Dolphin's servers and extract it. This might block your thread for a few seconds on the very first run.
* **LevelDB locks:** The token auto-fetcher reads the LevelDB database directly. If Dolphin is actively writing to it at the exact moment of instantiation, it might throw a read error. Just pass the token manually if this becomes an issue.