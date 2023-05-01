import argparse
import cmd
from .google_auth import authenticate
from .commands.base_command import BaseCommand

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
        args_list = line.split()
        command_name = args_list[0]

        # Create a new Namespace object containing the credentials and command arguments
        new_args = argparse.Namespace(**vars(self.args))
        new_args.command_args = args_list[1:]
        print(new_args)

        # Dynamically import the command module
        try:
            command_module = __import__(
                f"swat.commands.{command_name}",
                fromlist=["Command"],
            )
            command_class = getattr(command_module, "Command")
        except (ImportError, AttributeError):
            print(f"Error: Command '{command_name}' not found.")
            return

        # Check if the command class is a subclass of BaseCommand
        if not issubclass(command_class, BaseCommand):
            print(f"Error: Command '{command_name}' is not a valid command.")
            return

        # Instantiate and execute the command
        command = command_class(new_args)
        command.execute()


    def do_exit(self, arg):
        """Exit the shell."""
        print(""":: Until Next Time ::""")
        return True

    do_quit = do_exit

def main():
    parser = argparse.ArgumentParser(description="SWAT CLI")
    parser.add_argument("--credentials", help="Path to the credentials file", required=True)
    parser.add_argument("--token", help="Path to the token file", required=True)
    args = parser.parse_args()

    # Authenticate with Google Workspace
    scopes = ['https://www.googleapis.com/auth/admin.directory.user']
    creds = authenticate(scopes, args.credentials, args.token)

    # Start the interactive shell
    SWATShell(args).cmdloop()