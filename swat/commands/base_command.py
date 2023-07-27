
import argparse
import logging
from typing import List

from ..base import SWAT
from .. import utils


class BaseCommand:

    def __init__(self, command: str = None, args: List[str] = list, obj: SWAT = None) -> None:
        self.command = command
        self.args = args
        self.logger = logging.getLogger(__name__)
        self.obj = obj

    def execute(self) -> None:
        raise NotImplementedError("The 'execute' method must be implemented in each command class.")

    @classmethod
    def custom_help(cls) -> str:
        """Return custom help string."""
        raise NotImplementedError("The 'custom_help' method must be implemented in each command class.")

    @classmethod
    def load_parser(cls, *args, **kwargs) -> argparse.ArgumentParser:
        """Return custom parser."""
        return argparse.ArgumentParser(formatter_class=utils.CustomHelpFormatter, add_help=False, *args, **kwargs)
