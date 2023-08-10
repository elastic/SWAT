
import argparse
import json
import os
import platform
import sys
import zipfile
from pathlib import Path
from typing import List, Optional, Union

import requests
import yaml
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from tabulate import tabulate

ROOT_DIR = Path(__file__).parent.parent.absolute()
ETC_DIR = ROOT_DIR / 'swat' / 'etc'


class PathlibEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Path):
            return str(obj)


def load_etc_file(filename: str) -> Union[str, dict]:
    '''Load a  file from the etc directory.'''
    path = ETC_DIR / filename
    contents = path.read_text()
    if path.suffix == '.txt':
        return contents
    elif path.suffix == '.json':
        return json.loads(contents)
    elif path.suffix in ('.yaml', '.yml'):
        return yaml.safe_load(contents)

def check_file_exists(file: Path, error_message: str) -> None:
    '''Check if the given file exists, raise an error if it does not.'''
    if not file.exists():
        raise FileNotFoundError(f'{error_message}: {file}')
    if file.is_dir():
        raise IsADirectoryError(f'{error_message}: {file}')

def clear_terminal() -> None:
    '''Clear the terminal.'''
    os.system('cls' if sys.platform == 'windows' else 'clear')


def load_subparsers(parser: argparse.ArgumentParser, dest: str = 'subcommand') -> Optional[dict]:
    '''Load subparsers by name if they exist.'''
    for action in parser._actions:
        if action.dest != dest:
            continue
        return action.choices

def render_table(data: List[str], headers: List[str], table_format="fancy_grid"):
    '''Renders a table from the provided data and headers.'''
    table_data = [item.split(':') for item in data]
    table = tabulate(table_data, headers, tablefmt=table_format)
    return table

def download_chromedriver(destination_path: Path) -> Path:
    '''Download the appropriate ChromeDriver for the system and return its path.'''
    base_url = "https://chromedriver.storage.googleapis.com/"
    latest_version_url = f"{base_url}LATEST_RELEASE"

    # Get the latest ChromeDriver version
    response = requests.get(latest_version_url)
    version = response.text

    # Determine OS
    system = platform.system().lower()
    if system == 'windows':
        suffix = 'win32.zip'
    elif system == 'linux':
        suffix = 'linux64.zip'
    elif system == 'darwin':
        suffix = 'mac64.zip'
    else:
        raise Exception("Unsupported OS")

    # Download ChromeDriver
    url = f"{base_url}{version}/chromedriver_{suffix}"
    response = requests.get(url)

    # Write the downloaded content as a zip file
    zip_path = ETC_DIR / f"chromedriver_{suffix}"
    with zip_path.open('wb') as file:
        file.write(response.content)

    # Extract the zip file
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(destination_path)

    # Remove the zip file
    zip_path.unlink()

    # Set executable permission for the chromedriver binary (Unix-like systems)
    if system in ['linux', 'darwin']:
        chromedriver_path = destination_path / 'chromedriver'
        chromedriver_path.chmod(chromedriver_path.stat().st_mode | 0o111)

    return destination_path / 'chromedriver'

def get_chromedriver(chromedriver_path: Optional[Path] = None) -> webdriver.Chrome:
    '''Return a Chrome WebDriver instance, downloading ChromeDriver if necessary.'''
    chromedriver_path = chromedriver_path or ETC_DIR / 'chromedriver'

    if not chromedriver_path.exists():
        chromedriver_path = download_chromedriver(ETC_DIR)

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run Chrome in headless mode
    service = Service(executable_path=str(chromedriver_path))
    driver = webdriver.Chrome(service=service, options=options)

    return driver
