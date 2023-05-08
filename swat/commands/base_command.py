import yaml
import typing
from pathlib import Path

CONFIG_DIR =  Path().absolute() / "config.yaml"

class BaseCommand:
    def __init__(self, args: str) -> None:
        self.args = args
        self.config = yaml.safe_load(open(CONFIG_DIR, "r"))


    def execute(self) -> None:
        raise NotImplementedError("The 'execute' method must be implemented in each command class.")
