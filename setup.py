from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='selenium_dolphin',
    version='1.0.4',
    author='Maehdakvan',
    author_email='visitanimation@google.com',
    description='A Python module for controlling Dolphin browser profiles using Selenium/Pyppeteer. It also has a Dolphin API for creating, editing, and deleting profiles.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/DedInc/selenium_dolphin',
    project_urls={
        'Bug Tracker': 'https://github.com/DedInc/selenium_dolphin/issues',
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    packages=find_packages(),
    include_package_data = True,
    install_requires = ['requests', 'selenium', 'pyppeteer', 'pywinauto'],
    python_requires='>=3.6'
)