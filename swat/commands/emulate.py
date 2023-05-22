
import importlib
import os
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from typing import List

from swat.mixins import MarshmallowDataclassMixin
from swat.commands.base_command import BaseCommand


EMULATIONS_DIR = Path(__file__).parent.absolute() / 'emulations'


class Command(BaseCommand):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        assert len(self.args) > 0, "No emulation command provided."
        self.emulation_command, *self.args = self.args

    def execute(self) -> None:
        if self.emulation_command == "hello":
            print(f"hello {' '.join(self.args)}")
        elif self.emulation_command == "list-commands":
            print(' '.join(self.get_emulate_commands()))
        else:
            # Dynamically import the command module
            try:
                dotted_command = self.get_dotted_command_path(self.emulation_command)
                command_module = importlib.import_module(f"swat.commands.emulations.{dotted_command}")
                command_class = getattr(command_module, "Command")
            except (ImportError, AttributeError) as e:
                print(f"Error: Command '{self.emulation_command}' not found.")
                return

            # Check if the command class is a subclass of BaseCommand
            if not issubclass(command_class, BaseEmulationCommand):
                print(f"Error: Command '{self.emulation_command}' is not a valid command.")
                return

            try:
                # Instantiate and execute the command
                args = command_class.validate_and_build_args(self.args)
                command = command_class(**args)
                command.execute()
            except AssertionError as e:
                print(f"Error: {e}")

    @staticmethod
    def get_dotted_command_path(command_name: str) -> str:
        """Return the path to the command module."""
        path = list(EMULATIONS_DIR.rglob(f"{command_name}.py"))
        assert len(path) == 1, f"Error: Ambiguous command '{command_name}' more than one found with that name"
        dotted = str(path[0].relative_to(EMULATIONS_DIR)).replace(os.sep, '.')[:-3]
        return dotted

    @staticmethod
    def get_emulate_commands() -> List[str]:
        """Return a list of possible emulation commands."""
        commands = [c.stem for c in EMULATIONS_DIR.rglob('*.py') if not c.name.startswith('_')]
        return commands


@dataclass
class AttackMeta:
    tactic: str
    technique_ids: List[str]
    references: List[str]


@dataclass
class ArgsClass(MarshmallowDataclassMixin):
    """Argument validator class."""


class BaseEmulationCommand(Command):
    """Base class for all emulation commands."""

    meta: AttackMeta
    arg_class: ArgsClass

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        assert len(self.args) > 0, "No emulation command provided."
        self.emulation_command, *self.args = self.args

    def execute(self) -> None:
        if self.emulation_command == "hello":
            print(f"hello {' '.join(self.args)}")

    def get_arg_options(self) -> List[dict]:
        """Return a list of possible and required arguments for the command."""
        # TODO: may be better to just use marshmallow_dataclass to validate
        # [{
        #     'name' (jon.doe)
        #     'required'
        #     'type'

    @cached_property
    def validate_and_build_args(self) -> ArgsClass:
        """Validate that the arguments provided are valid."""
        return self.arg_class.from_dict(*self.args)

    def validate_meta(self):
        """Validate ATT&CK metadata."""
