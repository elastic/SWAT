#
# Licensed to Elasticsearch under one or more contributor
# license agreements. See the NOTICE file distributed with
# this work for additional information regarding copyright
# ownership. Elasticsearch licenses this file to you under
# the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#

"""Handle emulation commands."""

import importlib
import os
from pathlib import Path
from typing import Optional

from swat.commands.base_command import BaseCommand
from swat.emulations.base_emulation import BaseEmulation
from swat.utils import render_table

EMULATIONS_DIR = Path(__file__).parent.parent.absolute() / 'emulations'


class Command(BaseCommand):
    """Execute attack emulations."""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.emulation_command = None

        args = kwargs.pop('args', None)
        if args:
            self.emulation_name, *self.emulation_args = args
            if self.emulation_name not in self.get_emulate_commands():
                self.logger.info(f'Unknown emulation command: {self.emulation_name}')
            else:
                emulation_command_class = self.load_emulation_class(self.emulation_name)
                self.emulation_command = emulation_command_class(args=self.emulation_args, **kwargs)

    @classmethod
    def custom_help(cls) -> str:
        """Return the help message for the command."""
        emulations = cls.load_all_emulation_classes()
        emulation_details = [
            f'{emulation.name}:{emulation.__module__.split(".")[-1]}:'
            f'{emulation.parser.description}:{emulation.services}:'
            f'{emulation.scopes}:{emulation.techniques}'
            for emulation in emulations
        ]
        headers = ['name', 'emulation command', 'description', 'services', 'scopes', 'techniques']
        print(f'Available Emulations: \n{render_table(emulation_details, headers=headers)}')

    @staticmethod
    def get_dotted_command_path(command_name: str) -> str:
        """Return the path to the command module."""
        path = list(EMULATIONS_DIR.rglob(f'{command_name}.py'))
        assert len(path) == 1, f'Error: Ambiguous command "{command_name}" more than one found with that name'
        dotted = str(path[0].relative_to(EMULATIONS_DIR)).replace(os.sep, '.')[:-3]
        return dotted

    @staticmethod
    def get_emulate_commands() -> list[str]:
        """Return a list of possible emulation commands."""
        commands = [c.stem for c in EMULATIONS_DIR.rglob('*.py') if not c.name.startswith('_') and
                    not c.parent.name == 'emulations']
        return commands

    @classmethod
    def load_emulation_class(cls, name: str) -> Optional[type[BaseEmulation]]:
        # Dynamically import the command module
        try:
            dotted_command = cls.get_dotted_command_path(name)
            command_module = importlib.import_module(f'swat.emulations.{dotted_command}')
            command_class = getattr(command_module, 'Emulation')
        except (ImportError, AttributeError) as e:
            # TODO: fix
            self.logger.info(f'Error: Command "{name}" not found.')
            return

        # Check if the command class is a subclass of BaseCommand
        if not issubclass(command_class, BaseEmulation):
            # TODO: fix
            self.logger.info(f'Error: Command "{name}" is not a valid command.')
            return

        return command_class

    @classmethod
    def load_all_emulation_classes(cls) -> list[type[BaseEmulation]]:
        """Return a list of all available command classes."""
        return [cls.load_emulation_class(c) for c in cls.get_emulate_commands()]

    def execute(self) -> None:
        if not self.emulation_command:
            available_emulations = self.get_emulate_commands()
            for emulation in available_emulations:
                self.logger.info(emulation + '\n')
        else:
            self.logger.info(f'Executing emulation: {self.emulation_name}')
            self.emulation_command.execute()
