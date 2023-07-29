import json
import os
import sys
from pathlib import Path
from typing import Union

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
