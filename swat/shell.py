
import argparse
import cmd
import importlib
import logging
from pathlib import Path
from typing import Optional, Type, TypeVar

from . import utils
from .base import SWAT, Config
from .commands.base_command import BaseCommand
from .commands.emulate import Command as EmulateCommand
from .misc import CustomHelpFormatter, colorful_swat
from .utils import clear_terminal, format_scopes

ROOT_DIR = Path(__file__).parent.parent.absolute()
COMMANDS_DIR = ROOT_DIR / 'swat' / 'commands'
CONFIG_FILE = ROOT_DIR / 'swat' / 'etc' / 'config.yaml'

logo = """
░██████╗░██╗░░░░░░░██╗░█████╗░████████╗
██╔════╝░██║░░██╗░░██║██╔══██╗╚══██╔══╝
╚█████╗░░╚██╗████╗██╔╝███████║░░░██║░░░
░╚═══██╗░░████╔═████║░██╔══██║░░░██║░░░
██████╔╝░░╚██╔╝░╚██╔╝░██║░░██║░░░██║░░░
╚═════╝░░░░╚═╝░░░╚═╝░░╚═╝░░╚═╝░░░╚═╝░░░
:: Simple Workspace ATT&CK Tool ::
"""

T = TypeVar('T', bound=BaseCommand)
KEY = '\U0001F511'
USER = '\U0001F464'


class SWATShell(cmd.Cmd):
    intro = colorful_swat(logo)
    prompt = 'SWAT> '

    def __init__(self, args: argparse.Namespace) -> None:
        super().__init__()
        debug = args.__dict__.pop('debug')
        if debug:
            logging.info('Logging in debug mode.')

        self.args = args
        config = Config(CONFIG_FILE, args.custom_config)
        self.obj = SWAT(config)

        self._command_name = None
        self._new_args = None

        self.save_on_exit = self.obj.config.merged['settings'].get('save_on_exit', False)

        self._registered_commands = self._register_commands()

    def _register_commands(self) -> list[str]:
        """Register all commands in the commands directory."""
        commands = []
        for command in self.get_commands():
            # setattr(self, f'do_{command}', None)
            commands.append(command)
        return commands

    @staticmethod
    def get_commands() -> list[str]:
        """Return a list of possible commands."""
        commands = [c.stem for c in COMMANDS_DIR.rglob('*.py') if not c.name.startswith('_') and
                    not c.name in ('base_command.py',)]
        return commands

    @staticmethod
    def load_command(name: str) -> Optional[Type[T]]:
        """Dynamically import a command module."""
        try:
            command_module = importlib.import_module(f'swat.commands.{name}')
            command_class = getattr(command_module, 'Command')
        except (ImportError, AttributeError, ValueError, AssertionError) as e:
            logging.error(f'{e}')
            # raise AttributeError(f'Command '{name}' not found: {e}.')
            return

        return command_class

    def do_help(self, arg: str):
        """List available commands with 'help' or detailed help with 'help cmd'."""
        commands = self.get_commands()
        do_cmds = [n[3:] for n in self.get_names() if n.startswith('do_')]
        all_cmds = sorted(do_cmds + self._registered_commands)

        if arg:
            method = getattr(self, 'do_' + arg, None)
            if method:
                # if the do_ method exists, print its docstring
                if method.__doc__ is not None:
                    logging.info(f'{method.__doc__}\n')
                else:
                    logging.info(f'{self.nohelp % arg}\n')
            else:
                # load commands dynamically and get help based on the following precedence:
                #   1. custom_help() method defined in the command class
                #   2. parser defined in the command class
                #   3. docstring defined in the command class
                #   4. default missing help message

                arg, *remaining = arg.split()

                # custom handle nested `emulate` commands
                # Note: if there are subparsers (and subcommands) in emulations, support will need to be added to
                #   render those consistently, similar to below, where it is implemented for regular commands
                if arg.startswith('emulate') and len(remaining) > 0:
                    emulation = remaining[0] if remaining else None
                    if emulation in EmulateCommand.get_emulate_commands():
                        try:
                            command_class = EmulateCommand.load_emulation_class(emulation)
                        except AssertionError as e:
                            raise AssertionError(f'Emulation "{emulation}": {e}.')
                        logging.info(f'[{command_class.get_attack()}]\n{command_class.help()}')
                    else:
                        logging.info(f'Unrecognized emulation: {emulation}, options: '
                              f'{"|".join(EmulateCommand.get_emulate_commands())}\n')

                elif arg in commands:
                    command_class = self.load_command(arg)
                    custom_help = getattr(command_class, 'custom_help', None)
                    try:
                        custom = command_class.custom_help() if custom_help else None
                    except NotImplementedError:
                        custom = None

                    parser: argparse.ArgumentParser = getattr(command_class, 'parser', None)

                    if custom:
                            logging.info(f'{custom}')
                    elif parser:
                        subparsers = utils.load_subparsers(parser)
                        if remaining and remaining[0] in subparsers:
                            subparser = subparsers[remaining[0]]
                            subparser.formatter_class = CustomHelpFormatter
                            subparser.print_help()
                            print()
                        else:
                            parser.print_help()
                            print()
                    elif command_class.__doc__ is not None:
                        logging.info(f'{command_class.__doc__}\n')
                    else:
                        logging.info(f'{self.nohelp % arg}\n')
                else:
                    logging.info(f'unrecognized command: {arg}')
                    logging.info(f'{self.doc_leader}\n')
                    self.print_topics(self.doc_header, all_cmds, 15, 80)
            return
        else:
            # print a unified, sorted list of do_ and imported commands
            # this drops support for help_* topics
            logging.info(f'{self.doc_leader}\n')
            self.print_topics(self.doc_header, all_cmds, 15, 80)

    def emptyline(self) -> None:
        """Do nothing on empty line to replicate activity of non-do_ commands."""
        pass

    def precmd(self, line: str) -> str:
        """Handle pre-command processing."""
        line = line.strip()
        self._command_name, *args = line.split() if line else (None,)

        # Create a new Namespace object containing the credentials and command arguments
        self._new_args = dict(command=self._command_name, args=args)
        logging.info(f'Command execution: {self._new_args}')
        return line

    def postcmd(self, stop: bool, line: str) -> bool:
        """Handle post-command processing."""
        key = f'{KEY}' if self.obj.cred_store.store else ''
        self.prompt = f'SWAT{key}>' if key else 'SWAT>'
        return stop

    def default(self, line: str) -> any:
        """Handle commands that are not recognized."""
        command_class = self.load_command(self._command_name) if self._command_name else None
        if not command_class:
            return

        # Check if the command class is a subclass of BaseCommand
        if not issubclass(command_class, BaseCommand):
            logging.error(f'Error: Command "{self._command_name}" is not a valid command.')
            return

        try:
            # Instantiate and execute the command
            command = command_class(obj=self.obj, **self._new_args)
            command.execute()
        except Exception as e:
            logging.error(f'Error: {e}')

    @staticmethod
    def do_clear(arg: str) -> None:
        """Clear the screen."""
        clear_terminal()

    def do_toggle_cred_save(self, arg: str) -> None:
        """Toggle the saving of the cred store upon exiting the shell."""
        enabled = not self.save_on_exit
        self.save_on_exit = enabled
        logging.info(f'Save on exit enabled: {enabled}')

    def do_exit(self, arg: str) -> bool:
        """Exit the shell."""
        return True
