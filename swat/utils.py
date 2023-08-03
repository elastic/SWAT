
import argparse
import os
import sys
from pathlib import Path
from typing import Optional, Union

import json
import yaml


ROOT_DIR = Path(__file__).parent.parent.absolute()
ETC_DIR = ROOT_DIR / "swat" / "etc"


class PathlibEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Path):
            return str(obj)


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

def check_file_exists(file: Path, error_message: str) -> None:
    """Check if the given file exists, raise an error if it does not."""
    if not file.exists():
        raise FileNotFoundError(f"{error_message}: {file}")
    if file.is_dir():
        raise IsADirectoryError(f"{error_message}: {file}")

def clear_terminal() -> None:
    """Clear the terminal."""
    os.system("cls" if sys.platform == "windows" else "clear")


def load_subparsers(parser: argparse.ArgumentParser, dest: str = "subcommand") -> Optional[dict]:
    """Load subparsers by name if they exist."""
    for action in parser._actions:
        if action.dest != dest:
            continue
        return action.choices
