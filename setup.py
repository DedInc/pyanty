import sys
from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

install_requires = ['requests', 'selenium'] 

if sys.platform == 'win32':
    install_requires.append('pywinauto')

setup(
    name='pyanty',
    version='1.0.0',
    author='Maehdakvan',
    author_email='visitanimation@google.com',
    description='Python module for controlling Dolphin browser profiles using Selenium, Pyppeteer, and Playwright. Includes Dolphin API for profile management.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/DedInc/pyanty',
    project_urls={
        'Bug Tracker': 'https://github.com/DedInc/pyanty/issues',
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Microsoft :: Windows', 
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS',
    ],
    packages=find_packages(),
    include_package_data = True,
    install_requires = install_requires,
    python_requires='>=3.6'
)
