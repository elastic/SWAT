import argparse
import importlib
import typing
import glob
from dataclasses import dataclass

from mitreattack.stix20 import MitreAttackData

from swat.commands.base_command import BaseCommand

@dataclass
class AttackData:
    """Dataclass for ATT&CK Emulation"""
    tactic: str
    technique:  str


class Command(BaseCommand):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.kwargs = kwargs
        assert len(self.args) > 0, "No emulation command provided."
        self.attack = AttackData(self.args[0], self.args[1])

    def load_attack(self, attack: AttackData) -> any:
        try:
            attack_module = importlib.import_module(f"swat.commands.{attack.tactic}.{attack.technique}")
            command_module = getattr(attack_module, "Command")
            return command_module(**self.kwargs)
        except (ImportError, AttributeError) as e:
            self.logger.error(f"Attack module {attack} not found.")
            return None

    def execute(self) -> None:
        self.logger.info(f"Loading emulation for {self.attack}")
        emulate = self.load_attack(self.attack)
        emulate.execute(self.attack)

