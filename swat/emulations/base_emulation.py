
import logging
from argparse import ArgumentParser

from .. import utils
from ..base import SWAT


class BaseEmulation:
    def __init__(self, parser: ArgumentParser, args: list, obj: SWAT, **extra) -> None:
        self.obj = obj
        self.logger = logging.getLogger(__name__)
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
