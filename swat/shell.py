import argparse
import cmd
import importlib
import logging
from pathlib import Path


from . import utils
from .base import SWAT
from .commands.base_command import BaseCommand
from .utils import clear_terminal

ROOT_DIR = Path(__file__).parent.parent.absolute()
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

    def precmd(self, line: str) -> str:
        """Handle pre-command processing."""
        self._command_name, *args = line.split()

        # Create a new Namespace object containing the credentials and command arguments
        self._new_args = dict(command=self._command_name, args=args)
        return line


    def default(self, line: str) -> any:
        """Handle commands that are not recognized."""
        # Dynamically import the command module
        try:
            command_module = importlib.import_module(f"swat.commands.{self._command_name}")
            command_class = getattr(command_module, "Command")
        except (ImportError, AttributeError, ValueError) as e:
            logging.error(f"{e}")
            # TODO: print available commands
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
