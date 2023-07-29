
import argparse
import cmd
import importlib
import logging
from pathlib import Path
from typing import Optional, Type, TypeVar

from . import utils
from .base import SWAT
from .commands.base_command import BaseCommand
from .commands.emulate import Command as EmulateCommand
from .misc import CustomHelpFormatter
from .utils import clear_terminal

ROOT_DIR = Path(__file__).parent.parent.absolute()
COMMANDS_DIR = ROOT_DIR / "swat" / "commands"
DEFAULT_TOKEN_FILE = ROOT_DIR / "token.pickle"
DEFAULT_CRED_FILE = ROOT_DIR / "credentials.json"
CONFIG: dict = utils.load_etc_file("config.yaml")


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


class SWATShell(cmd.Cmd):

    intro = logo
    prompt = "SWAT> "

    def __init__(self, args: argparse.Namespace) -> None:
        super().__init__()
        debug = args.__dict__.pop("debug")
        if debug:
            logging.info("Logging in debug mode.")

        self.args = args

        self.obj = SWAT(CONFIG, args.credentials, args.token)

        self._command_name = None
        self._new_args = None

        self._registered_commands = self._register_commands()

    def _register_commands(self) -> list[str]:
        """Register all commands in the commands directory."""
        commands = []
        for command in self.get_commands():
            # setattr(self, f"do_{command}", None)
            commands.append(command)
        return commands

    @staticmethod
    def get_commands() -> list[str]:
        """Return a list of possible commands."""
        commands = [c.stem for c in COMMANDS_DIR.rglob('*.py') if not c.name.startswith('_') and
                    not c.name in ("base_command.py",)]
        return commands

    @staticmethod
    def load_command(name: str) -> Optional[Type[T]]:
        """Dynamically import a command module."""
        try:
            command_module = importlib.import_module(f"swat.commands.{name}")
            command_class = getattr(command_module, "Command")
        except (ImportError, AttributeError, ValueError, AssertionError) as e:
            logging.error(f"{e}")
            # raise AttributeError(f"Command '{name}' not found: {e}.")
            return

        return command_class

    def do_help(self, arg: str):
        """List available commands with "help" or detailed help with "help cmd"."""
        commands = self.get_commands()
        do_cmds = [n[3:] for n in self.get_names() if n.startswith("do_")]
        all_cmds = sorted(do_cmds + self._registered_commands)

        if arg:
            method = getattr(self, 'do_' + arg, None)
            if method:
                # if the do_ method exists, print its docstring
                if method.__doc__ is not None:
                    print(f"{method.__doc__}\n")
                else:
                    print(f"{self.nohelp % arg}\n")
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
                if arg.startswith('emulate') and len(arg.split()) > 1:
                    emulation = remaining[0] if remaining else None
                    if emulation in EmulateCommand.get_emulate_commands():
                        try:
                            command_class = EmulateCommand.load_emulation_class(emulation)
                        except AssertionError as e:
                            raise AssertionError(f"Emulation '{emulation}': {e}.")
                        print(f"[{command_class.get_attack()}]\n{command_class.help()}")
                    else:
                        print(f"Unrecognized emulation: {emulation}, options: "
                              f"{'|'.join(EmulateCommand.get_emulate_commands())}\n")

                elif arg in commands:
                    command_class = self.load_command(arg)
                    custom_help = getattr(command_class, "custom_help", None)
                    try:
                        custom = command_class.custom_help() if custom_help else None
                    except NotImplementedError:
                        custom = None

                    parser: argparse.ArgumentParser = getattr(command_class, "parser", None)

                    if custom:
                        print(f"{custom}\n")
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
                        print(f"{command_class.__doc__}\n")
                    else:
                        print(f"{self.nohelp % arg}\n")
                else:
                    print(f"unrecognized command: {arg}")
                    print(f"{self.doc_leader}\n")
                    self.print_topics(self.doc_header, all_cmds, 15, 80)
            return
        else:
            # print a unified, sorted list of do_ and imported commands
            # this drops support for help_* topics
            print(f"{self.doc_leader}\n")
            self.print_topics(self.doc_header, all_cmds, 15, 80)


    def precmd(self, line: str) -> str:
        """Handle pre-command processing."""
        self._command_name, *args = line.split()

        # Create a new Namespace object containing the credentials and command arguments
        self._new_args = dict(command=self._command_name, args=args)
        return line


    def default(self, line: str) -> any:
        """Handle commands that are not recognized."""
        command_class = self.load_command(self._command_name)
        if not command_class:
            return

        # Check if the command class is a subclass of BaseCommand
        if not issubclass(command_class, BaseCommand):
            logging.error(f"Error: Command '{self._command_name}' is not a valid command.")
            return

        try:
            # Instantiate and execute the command
            command = command_class(obj=self.obj, **self._new_args)
            command.execute()
        except Exception as e:
            logging.error(f"Error: {e}")

    @staticmethod
    def do_clear(self, arg: str) -> None:
        """Clear the screen."""
        clear_terminal()

    def do_exit(self, arg: str) -> bool:
        """Exit the shell."""
        print(""":: Until Next Time ::""")
        return True
