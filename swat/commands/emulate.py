import argparse
import glob
import importlib
import typing
from dataclasses import dataclass
from pathlib import Path

from mitreattack.stix20 import MitreAttackData

from swat.commands.base_command import BaseCommand

EMULATIONS_DIR = Path(__file__).parent.parent.absolute() / 'emulations'
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
        emulation_commands = [c for c in self.args if c.replace("-","_") in
                              Command.__dict__ or c == "list-commands"]
        if emulation_commands:
            self.command = emulation_commands[0].replace("-","_")
            self.attack = None
        else:
            assert len(self.args) > 1, "No emulation command provided."
            self.attack = AttackData(self.args[0], self.args[1])
            self.command = "emulate"


    def load_attack(self, attack: AttackData) -> any:
        try:
            attack_module = importlib.import_module(f"swat.emulations.{attack.tactic}.{attack.technique}")
            emulation_module = getattr(attack_module, "Emulation")
            return emulation_module(tactic=attack.tactic,
                                    technique=attack.technique,
                                    **self.kwargs)
        except (ImportError, AttributeError) as e:
            self.logger.error(f"Emulation module {attack} not found.")
            return None


    def list_commands(self):
        """List all available commands"""
        commands = [method.replace("_", "-") for method in dir(self) if not method.startswith("_")
                    and callable(getattr(self, method)) and method != "execute"
                    and method != "list_commands" and method != "load_attack"]
        return '|'.join(commands)


    @staticmethod
    def list_tactics(**kwargs):
        """List all available tactics"""
        tactics = "|".join([tactic.name for tactic in EMULATIONS_DIR.iterdir() if
                   tactic.is_dir() and not tactic.name.startswith('_')])
        return tactics


    @staticmethod
    def list_techniques(**kwargs):
        """List all available techniques for a given tactic"""
        tactic = kwargs.get('args')[1]
        tactic_dir = EMULATIONS_DIR / tactic
        if not tactic_dir.exists():
            return f"No techniques found for tactic: {tactic}"
        techniques = '|'.join([technique.stem for technique in tactic_dir.glob('*.py')
                    if technique.stem != '__init__'])
        return techniques


    def execute(self) -> None:
        if self.attack is not None:
            self.logger.info(f"Loading emulation for {self.attack}")
            emulate = self.load_attack(self.attack)
            emulate.execute()
        elif self.command == "list_commands":
            self.logger.info(f"Available commands - {self.list_commands()}")
        else:
            self.logger.info(f"Executing command - {self.command}")
            self.logger.info(f"Command results - {getattr(self, self.command)(args=self.args)}")

