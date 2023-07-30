
import argparse
import logging
from dataclasses import dataclass
from functools import cache
from typing import Optional

from ..attack import lookup_technique_by_id
from ..base import SWAT
from ..misc import get_custom_argparse_formatter, validate_args


@dataclass
class AttackData:
    """Dataclass for ATT&CK Emulation"""
    tactic: str
    technique: list[str]
    _emulation_name: str
    _emulation_description: str

    def __str__(self) -> str:
        return f"{self.tactic}: {', '.join(self.technique)}"

    def _raw_technique_details(self) -> dict:
        """Get technique details from ATT&CK."""
        return {t: lookup_technique_by_id(t) for t in self.technique}

    def technique_details(self) -> dict:
        """Print technique details."""
        all_details = {}

        raw = self._raw_technique_details()
        for technique, details in raw.items():
            if not details:
                raise ValueError(f"Technique {technique} not found in ATT&CK data.")
            else:
                data = {
                    'id': technique,
                    'tactic': self.tactic,
                    'name': details.get('name'),
                    'description': details['description'].split('.')[0].strip(),
                    'emulation': self._emulation_name,
                    'emulation_description': self._emulation_description
                }
                all_details[technique] = data

        return all_details


class BaseEmulation:

    parser: Optional[argparse.ArgumentParser]
    techniques: list[str]

    def __init__(self, args: list, obj: SWAT, **extra) -> None:
        self.obj = obj
        self.logger = logging.getLogger(__name__)
        self.attack_data = self.get_attack()

        assert self.parser, "'parser' must be implemented in each emulation command class"
        self.args = validate_args(self.parser, args)
        assert hasattr(self, "techniques"), "'techniques' must be implemented in each emulation command class (or [])"

    def execute(self) -> None:
        raise NotImplementedError("The 'execute' method must be implemented in each emulation class.")

    @classmethod
    @cache
    def get_attack(cls) -> AttackData:
        """Parse tactic and technique from path."""
        _, _, tactic, emulation_name = cls.__module__.split('.')
        techniques = [t.upper() for t in cls.techniques]
        return AttackData(tactic=tactic, technique=techniques, _emulation_name=emulation_name,
                          _emulation_description=cls.parser.description)

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
