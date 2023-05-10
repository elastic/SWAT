import argparse
import cmd
import importlib
import logging
import os
import sys
import typing
from pathlib import Path

from swat import utils
from swat.commands.base_command import BaseCommand

ROOT_DIR = Path(__file__).parent.parent.absolute()
DEFAULT_TOKEN_FILE = ROOT_DIR / "token.pickle"
DEFAULT_CRED_FILE = ROOT_DIR / "credentials.json"
CONFIG: dict = utils.load_etc_file("config.yaml")

class SWATShell(cmd.Cmd):
    intro = """
░██████╗░██╗░░░░░░░██╗░█████╗░████████╗
██╔════╝░██║░░██╗░░██║██╔══██╗╚══██╔══╝
╚█████╗░░╚██╗████╗██╔╝███████║░░░██║░░░
░╚═══██╗░░████╔═████║░██╔══██║░░░██║░░░
██████╔╝░░╚██╔╝░╚██╔╝░██║░░██║░░░██║░░░
╚═════╝░░░░╚═╝░░░╚═╝░░╚═╝░░╚═╝░░░╚═╝░░░
:: Simple Workspace ATT&CK Tool ::
\n"""
    prompt = "SWAT> "

    def __init__(self, args: argparse.Namespace) -> None:
        super().__init__()
        self.args = args

    def default(self, line: str) -> None:
        """Handle commands that are not recognized."""
        args_list = line.split()
        command_name = args_list[0]

        # Create a new Namespace object containing the credentials and command arguments
        new_args = dict(command=command_name, args=args_list[1:], config=CONFIG, **(vars(self.args)))

        # Dynamically import the command module
        try:
            command_module = importlib.import_module(f"swat.commands.{command_name}")
            command_class = getattr(command_module, "Command")
        except (ImportError, AttributeError) as e:
            logging.error(f"Command '{command_name}' not found.")
            return

        # Check if the command class is a subclass of BaseCommand
        if not issubclass(command_class, BaseCommand):
            logging.error(f"Error: Command '{command_name}' is not a valid command.")
            return

        try:
            # Instantiate and execute the command
            command = command_class(**new_args)
            command.execute()
        except AssertionError as e:
            logging.error(f"Error: {e}")

    def do_authenticate(self, arg: str) -> None:
        """Authenticate to the Google Workspace"""
        self.default(f"authenticate {arg}")

    def do_coverage(self, arg: str) -> None:
        """Display ATT&CK coverage."""
        self.default(f"coverage {arg}")

    def do_emulate(self, arg: str) -> None:
        """Emulate ATT&CK techniques."""
        self.default(f"emulate {arg}")


    def do_exit(self, arg: str) -> bool:
        """Exit the shell."""
        print(""":: Until Next Time ::""")
        return True
