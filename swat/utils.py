
import gzip
import json
import os
import sys
from functools import lru_cache
from pathlib import Path
from typing import Union

import requests
import yaml


ROOT_DIR = Path(__file__).parent.parent.absolute()
ETC_DIR = ROOT_DIR / "swat" / "etc"


def load_etc_file(filename: str) -> Union[str, dict]:
    """Load a  file from the etc directory."""
    path = ETC_DIR / filename
    contents = path.read_text()
    if path.suffix == ".txt":
        return contents
    elif path.suffix == ".json":
        return json.loads(contents)
    elif path.suffix in (".yaml", ".yml"):
        return yaml.safe_load(contents)


def clear_terminal() -> None:
    """Clear the terminal."""
    os.system("cls" if sys.platform == "windows" else "clear")


def validate_args(parser, args):
    """Parse arguments."""
    try:
        parsed_args, unknown = parser.parse_known_args(args)
        if unknown:
            raise ValueError(f"Unknown arguments {unknown}")
    except SystemExit:
        return None
    return parsed_args


def download_attack_data() -> None:
    """Download the ATT&CK data from the MITRE CTI repo."""
    url = "https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json"
    response = requests.get(url)
    response.raise_for_status()
    gzip_file_path = ETC_DIR / "enterprise-attack.json.gz"
    compressed_content = gzip.compress(response.content)
    gzip_file_path.write_bytes(compressed_content)


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
def lookup_technique_by_id(technique_id) -> str | None:
    """Look up a technique by ID in ATT&CK enterprise data."""
    data = load_attack_data()
    for item in data["objects"]:
        if item["type"] == "attack-pattern":
            if "external_references" in item:
                for ref in item["external_references"]:
                    if ref["source_name"] == "mitre-attack" and ref["external_id"] == technique_id:
                        return item
