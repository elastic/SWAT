
import gzip
import json
import logging
from functools import lru_cache
from typing import Optional

import requests
from semver import Version

from swat.utils import ETC_DIR

ATTACK_PATH = ETC_DIR / "enterprise-attack.json.gz"


def download_attack_data(save: bool = True) -> (Optional[dict], Optional[bytes]):
    """Refresh ATT&CK data from Mitre."""

    def get_version_from_tag(name, pattern='att&ck-v'):
        _, version = name.lower().split(pattern, 1)
        return version

    current_version = load_attack_data()['version'] if ATTACK_PATH.exists() else None

    r = requests.get('https://api.github.com/repos/mitre/cti/tags')
    r.raise_for_status()
    releases = [t for t in r.json() if t['name'].startswith('ATT&CK-v')]
    latest_release = max(releases, key=lambda release: Version.parse(get_version_from_tag(release['name']),
                         optional_minor_and_patch=True))
    release_name = latest_release['name']
    latest_version = Version.parse(get_version_from_tag(release_name), optional_minor_and_patch=True)

    if current_version and current_version >= latest_version:
        logging.info(f'ATT&CK version: {current_version} is up to date.')
        return None, None

    download = f'https://raw.githubusercontent.com/mitre/cti/{release_name}/enterprise-attack/enterprise-attack.json'
    r = requests.get(download)
    r.raise_for_status()
    attack_data = r.json()
    data = {'version': str(latest_version), 'data': attack_data}
    compressed = gzip.compress(json.dumps(data, sort_keys=True).encode())

    if save:
        ATTACK_PATH.write_bytes(compressed)
        logging.info(f'ATT&CK version: {latest_version} saved to: {ATTACK_PATH}')

    return attack_data, compressed


@lru_cache(maxsize=1)
def load_attack_data() -> dict:
    """Load the ATT&CK data from local file."""
    gzip_file_path = ETC_DIR / "enterprise-attack.json.gz"
    if not gzip_file_path.exists():
        download_attack_data()
    with gzip.open(gzip_file_path, 'rb') as file:
        attack_data = json.load(file)

    return attack_data


@lru_cache(maxsize=128)
def lookup_technique_by_id(technique_id: str) -> Optional[dict]:
    """Look up a technique by ID in ATT&CK enterprise data."""
    data = load_attack_data()['data']
    for item in data["objects"]:
        if item["type"] == "attack-pattern":
            if "external_references" in item:
                for ref in item["external_references"]:
                    if ref["source_name"] == "mitre-attack" and ref["external_id"] == technique_id:
                        return item
