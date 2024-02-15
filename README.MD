# 🐬 selenium-dolphin

A Python module for controlling Dolphin browser profiles using Selenium or Pyppeteer 🤖. It also has a Dolphin API for creating, editing, and deleting profiles.

## ⚠️ Warning!

```
Selenium and some features working only if Dolphin Anty is opened!!! (Local API wrapper must be launched!)
```

## 🚀 Quickstart

### Selenium

```python
import random
import selenium_dolphin as dolphin
from selenium_dolphin import DolphinAPI, STABLE_CHROME_VERSION
from selenium.webdriver.chrome.options import Options

api = DolphinAPI(api_key='Your Api Key')

response = api.get_profiles()
if response['data']:
    profile_id = response['data'][-1]['id']
    if profile_id:
        api.delete_profiles([profile_id])

fingerprint = []
while not fingerprint:
  fingerprint = api.generate_fingerprint(platform='windows', browser_version=f'{random.randint(114, STABLE_CHROME_VERSION)}')

data = api.fingerprint_to_profile(name='my superprofile', fingerprint=fingerprint)

profile_id = api.create_profile(data)['browserProfileId']

response = dolphin.run_profile(profile_id)
port = response['automation']['port']

##### custom chrome options demonstration #####
options = Options()
options.add_argument("--start-maximized")
###############################################

driver = dolphin.get_driver(options=options, port=port)
driver.get('https://google.com/')
print(driver.title)
driver.quit()

dolphin.close_profile(profile_id)
```

### Pyppeteer

```python
import asyncio
import random
import selenium_dolphin as dolphin
from selenium_dolphin import DolphinAPI, STABLE_CHROME_VERSION

api = DolphinAPI(api_key='Your Api Key')

response = api.get_profiles()
if response['data']:
    profile_id = response['data'][-1]['id']
    if profile_id:
        api.delete_profiles([profile_id])

fingerprint = []
while not fingerprint:
  fingerprint = api.generate_fingerprint(platform='windows', browser_version=f'{random.randint(114, STABLE_CHROME_VERSION)}')

data = api.fingerprint_to_profile(name='my superprofile', fingerprint=fingerprint)

profile_id = api.create_profile(data)['browserProfileId']

response = dolphin.run_profile(profile_id)
port = response['automation']['port']
ws_endpoint = response['automation']['wsEndpoint']

async def main():
    browser = await dolphin.get_browser(ws_endpoint, port)
    pages = await browser.pages()
    page = pages[0]
    await page.goto('http://google.com/')
    await asyncio.sleep(5)
    await browser.disconnect()

asyncio.run(main())
dolphin.close_profile(profile_id)
```

## 📝 Get profiles

```python
from selenium_dolphin import DolphinAPI

api = DolphinAPI() # you can enter api_key='Your key' inside instance
```

You can [get an API key here](https://dolphin-anty.com/panel/#/api), but if the token is present in the logs, the module can automatically retrieve it.

```python
response = api.get_profiles() 

print(response)
```

### Pagination and limitation

```python
response = api.get_profiles(page=1, limit=300) # default page - 1 limit - 50
```

## 🆕 Create profile

```python
fingerprint = api.generate_fingerprint(platform='linux') # you can use platform windows/linux/macos, also you can use screen='1366x768' and browser_version='116' if you need

data = api.fingerprint_to_profile(name='my profile', fingerprint=fingerprint) # also you can add tags=['test', 'selenium_dolphin'] and other

response = api.create_profile(data)  

print(response)
```

## 📝 Custom data for profile

After this line:

```python
data = api.fingerprint_to_profile(name='my profile', fingerprint=fingerprint)
```

Use for:

### Geolocation 🗺️

```python
data.update({'geolocation':{
  'mode': 'manual',
  'latitude': 33.4,
  'longitude': 55.2,
  'accuracy': 318
}})
```

### Timezone ⏰

```python
data.update({'timezone':{
  'mode':'manual',
  'value':'Pacific/Johnston'
}})
```

### Locale 🌎

```python
data.update({'locale':{
  'mode':'manual',
  'value':'af_ZA' 
}})
```

### Proxy 🕸️

```python
data.update({'proxy':{
  'name': 'http://37.19.220.129:8443',
  'host': '37.19.220.129',
  'port': '8443',
  'type': 'http' 
}})
# also you can add 'login' and 'password' args
```

### and others...

## ✏️ Edit profile

```python 
from selenium_dolphin import DolphinAPI

api = DolphinAPI()

fingerprint = api.generate_fingerprint(platform='windows') 

data = api.fingerprint_to_profile(name='mega profile', fingerprint=fingerprint)

response = api.edit_profile(190438486, data)

print(response)
```

## 🗑️ Delete profile(s)

```python
from selenium_dolphin import DolphinAPI

api = DolphinAPI()

response = api.delete_profiles([190438486]) # you need specify list ids of profiles  

print(response)
```

## 🔍 Other features

### Proxy checker

```python
response = api.check_proxy(host='37.19.220.129', port='8443', type='http')

print(response)

# also you can use other kwargs (login='username', password='password')
```

Response:

```json
{"success": true, "country": "US", "region": "Virginia", "city": "Ashburn", "ip": "37.19.220.178", "timezone": "America/New_York"}
```

### MAC Address generator

```python
response = api.generate_mac()  

print(response) 
```

Response:

```json
{"success": true, "macAddress": "8E:DD:48:08:F1:31"}
```

## Conclusion

selenium-dolphin provides a straightforward way to control Dolphin browser profiles for automation testing using Selenium or Pyppeteer 🤖. With the Dolphin API, you can easily create, customize, and manage profiles right from Python. Give it a try for your next web scraping or test automation project! 🐬