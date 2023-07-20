
import logging
from argparse import ArgumentParser
from pathlib import Path

from .. import utils


class BaseEmulation:
    def __init__(self, credentials: Path, token: Path, config: dict, parser: ArgumentParser, args: list,
                 **extra) -> None:
        self.config = config
        self.credentials = credentials
        self.token = token
        self.logger = logging.getLogger(__name__)
        self.creds = extra['creds']

        self.tactic, self.technique = self.parse_attack_from_class()

        self.args = utils.validate_args(parser, args)


    def execute(self) -> None:
        raise NotImplementedError("The 'execute' method must be implemented in each emulation class.")

    def parse_attack_from_class(self) -> (str, str):
        """Parse tactic and technique from path."""
        _, _, tactic, technique = self.__module__.split('.')
        return tactic, technique.upper()

    def exec_str(self, description: str) -> str:
        """Return standard execution log string."""
        return f"Executing emulation for: [{self.tactic} - {self.technique}] {description}"
