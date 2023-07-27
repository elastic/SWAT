
import argparse
import logging
from typing import Optional

from .. import utils
from ..base import SWAT


class BaseEmulation:

    parser: Optional[argparse.ArgumentParser] = None

    def __init__(self, args: list, obj: SWAT, **extra) -> None:
        self.obj = obj
        self.logger = logging.getLogger(__name__)
        self.tactic, self.technique = self.parse_attack_from_class()

        assert self.parser, "'parser' must be implemented in each emulation command class"
        self.args = utils.validate_args(self.parser, args)

    def execute(self) -> None:
        raise NotImplementedError("The 'execute' method must be implemented in each emulation class.")

    def parse_attack_from_class(self) -> (str, str):
        """Parse tactic and technique from path."""
        _, _, tactic, technique = self.__module__.split('.')
        return tactic, technique.upper()

    def exec_str(self, description: str) -> str:
        """Return standard execution log string."""
        return f"Executing emulation for: [{self.tactic} - {self.technique}] {description}"

    @classmethod
    def help(cls):
        """Return the help message for the command."""
        assert cls.parser, "'parser' must be implemented in each emulation command class"
        return cls.parser.format_help()

    @classmethod
    def load_parser(cls, *args, **kwargs) -> argparse.ArgumentParser:
        """Return custom parser."""
        return argparse.ArgumentParser(formatter_class=utils.CustomHelpFormatter, add_help=False, *args, **kwargs)
