
import argparse
import logging
from dataclasses import dataclass
from functools import cache
from typing import Optional

from ..base import SWAT
from ..misc import get_custom_argparse_formatter, validate_args


@dataclass
class AttackData:
    """Dataclass for ATT&CK Emulation"""
    tactic: str
    technique: list[str]

    def __str__(self) -> str:
        return f"{self.tactic}: {', '.join(self.technique)}"


class BaseEmulation:

    parser: Optional[argparse.ArgumentParser]
    techniques: list[str]

    def __init__(self, args: list, obj: SWAT, **extra) -> None:
        self.obj = obj
        self.logger = logging.getLogger(__name__)
        self.attack_data = self.parse_attack_from_class()

        assert self.parser, "'parser' must be implemented in each emulation command class"
        self.args = validate_args(self.parser, args)
        assert hasattr(self, "techniques"), "'techniques' must be implemented in each emulation command class (or [])"

    def execute(self) -> None:
        raise NotImplementedError("The 'execute' method must be implemented in each emulation class.")

    @classmethod
    @cache
    def parse_attack_from_class(cls) -> AttackData:
        """Parse tactic and technique from path."""
        _, _, tactic, _ = cls.__module__.split('.')
        techniques = [t.upper() for t in cls.techniques]
        return AttackData(tactic=tactic, technique=techniques)

    def exec_str(self, description: str) -> str:
        """Return standard execution log string."""
        return f"Executing emulation for: [{self.attack_data}] {description}"

    @classmethod
    def help(cls):
        """Return the help message for the command."""
        assert cls.parser, "'parser' must be implemented in each emulation command class"
        return cls.parser.format_help()

    @classmethod
    def load_parser(cls, *args, **kwargs) -> argparse.ArgumentParser:
        """Return custom parser."""
        return get_custom_argparse_formatter(*args, **kwargs)
