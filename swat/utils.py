#
# Licensed to Elasticsearch under one or more contributor
# license agreements. See the NOTICE file distributed with
# this work for additional information regarding copyright
# ownership. Elasticsearch licenses this file to you under
# the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#

import argparse
import json
import os
import platform
import sys
import zipfile
from pathlib import Path
from typing import List, Optional, Union
from textwrap import wrap

import requests
import yaml
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from tabulate import tabulate

ROOT_DIR = Path(__file__).parent.parent.absolute()
ETC_DIR = ROOT_DIR / 'swat' / 'etc'
DEFAULT_EMULATION_ARTIFACTS_DIR = ETC_DIR / 'artifacts'


class PathlibEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Path):
            return str(obj)


def load_etc_file(filename: str) -> Union[str, dict]:
    """Load a  file from the etc directory."""
    path = ETC_DIR / filename
    contents = path.read_text()
    if path.suffix == '.txt':
        return contents
    elif path.suffix == '.json':
        return json.loads(contents)
    elif path.suffix in ('.yaml', '.yml'):
        return yaml.safe_load(contents)

def check_file_exists(file: Path, error_message: str) -> None:
    """Check if the given file exists, raise an error if it does not."""
    if not file.exists():
        raise FileNotFoundError(f'{error_message}: {file}')
    if file.is_dir():
        raise IsADirectoryError(f'{error_message}: {file}')

def clear_terminal() -> None:
    """Clear the terminal."""
    os.system('cls' if sys.platform == 'windows' else 'clear')


def load_subparsers(parser: argparse.ArgumentParser, dest: str = 'subcommand') -> Optional[dict]:
    """Load subparsers by name if they exist."""
    for action in parser._actions:
        if action.dest != dest:
            continue
        return action.choices

def render_table(data: List[str], headers: List[str], table_format="fancy_grid", max_width=30):
    """Renders a table from the provided data and headers, wrapping text if it exceeds max_width."""

    def wrap_text(text):
        '''Wrap text if it exceeds max_width.'''
        return '\n'.join(wrap(text, max_width))

    table_data = [[wrap_text(cell) for cell in item.split(':')] for item in data]
    wrapped_headers = [wrap_text(header) for header in headers]
    table = tabulate(table_data, wrapped_headers, tablefmt=table_format)
    return table

def download_chromedriver(destination_path: Path) -> Path:
    """Download the appropriate ChromeDriver for the system and return its path."""
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
    """Return a Chrome WebDriver instance, downloading ChromeDriver if necessary."""
    chromedriver_path = chromedriver_path or ETC_DIR / 'chromedriver'

    if not chromedriver_path.exists():
        chromedriver_path = download_chromedriver(ETC_DIR)

    options = webdriver.ChromeOptions()

    DEFAULT_EMULATION_ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    options.add_experimental_option('prefs', {
    "download.default_directory": str(DEFAULT_EMULATION_ARTIFACTS_DIR), # set the download directory
    "download.prompt_for_download": False, # disable download prompt
})
    options.add_argument('--headless')  # Run Chrome in headless mode

    service = Service(executable_path=str(chromedriver_path))
    driver = webdriver.Chrome(service=service, options=options)

    return driver

def format_scopes(scopes: Union[str, List[str]]) -> List[str]:
    """Format a list of scopes for display."""
    if isinstance(scopes, str):
        return f'https://www.googleapis.com/auth/{scopes}' \
               if 'https://www.googleapis.com/auth/' not in scopes else scopes
    else:
        return [f'https://www.googleapis.com/auth/{scope}' for
                scope in scopes if 'https://www.googleapis.com/auth/' not in scope]