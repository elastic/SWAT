import argparse
import cmd
import importlib
import os
import sys
import typing
from pathlib import Path

import yaml

from swat.commands.base_command import BaseCommand
from swat.google_auth import authenticate

CONFIG_DIR =  Path().absolute() / "config.yaml"

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

    def __init__(self, args):
        super().__init__()
        self.args = args

    def default(self, line):
        """Handle commands that are not recognized."""
        args_list = line.split()
        command_name = args_list[0]

        # Create a new Namespace object containing the credentials and command arguments
        new_args = argparse.Namespace(**vars(self.args))
        new_args.command_args = args_list[1:]

        # Dynamically import the command module
        try:
            command_module = importlib.import_module(f"swat.commands.{command_name}")
            command_class = getattr(command_module, "Command")
        except (ImportError, AttributeError) as e:
            print(f"Error: Command '{command_name}' not found.")
            return

        # Check if the command class is a subclass of BaseCommand
        if not issubclass(command_class, BaseCommand):
            print(f"Error: Command '{command_name}' is not a valid command.")
            return

        # Instantiate and execute the command
        command = command_class(new_args)
        command.execute()


    def do_coverage(self, arg):
        """Display ATT&CK coverage."""
        self.default(f"coverage {arg}")


    def do_emulate(self, arg):
        """Emulate ATT&CK techniques."""
        self.default(f"emulate {arg}")


    def do_exit(self, arg):
        """Exit the shell."""
        print(""":: Until Next Time ::""")
        return True


def main():
    parser = argparse.ArgumentParser(description="SWAT CLI")
    parser.add_argument("--credentials", help="Path to the credentials file", required=True)
    parser.add_argument("--token", help="Path to the token file", required=True)
    args = parser.parse_args()

    # Authenticate with Google Workspace
    scopes = yaml.safe_load(CONFIG_DIR.open())['google']['scopes']
    creds = authenticate(scopes, args.credentials, args.token)

    # Start the interactive shell
    SWATShell(args).cmdloop()


if __name__ == "__main__":
    main()