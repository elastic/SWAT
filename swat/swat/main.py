import argparse
import cmd
from .google_auth import authenticate
from .commands.base_command import BaseCommand

class SWATShell(cmd.Cmd):
    intro = """
░██████╗██╗███╗░░░███╗██████╗░██╗░░░░░███████╗
██╔════╝██║████╗░████║██╔══██╗██║░░░░░██╔════╝
╚█████╗░██║██╔████╔██║██████╔╝██║░░░░░█████╗░░
░╚═══██╗██║██║╚██╔╝██║██╔═══╝░██║░░░░░██╔══╝░░
██████╔╝██║██║░╚═╝░██║██║░░░░░███████╗███████╗
╚═════╝░╚═╝╚═╝░░░░░╚═╝╚═╝░░░░░╚══════╝╚══════╝

░██╗░░░░░░░██╗░█████╗░██████╗░██╗░░██╗░██████╗██████╗░░█████╗░░█████╗░███████╗
░██║░░██╗░░██║██╔══██╗██╔══██╗██║░██╔╝██╔════╝██╔══██╗██╔══██╗██╔══██╗██╔════╝
░╚██╗████╗██╔╝██║░░██║██████╔╝█████═╝░╚█████╗░██████╔╝███████║██║░░╚═╝█████╗░░
░░████╔═████║░██║░░██║██╔══██╗██╔═██╗░░╚═══██╗██╔═══╝░██╔══██║██║░░██╗██╔══╝░░
░░╚██╔╝░╚██╔╝░╚█████╔╝██║░░██║██║░╚██╗██████╔╝██║░░░░░██║░░██║╚█████╔╝███████╗
░░░╚═╝░░░╚═╝░░░╚════╝░╚═╝░░╚═╝╚═╝░░╚═╝╚═════╝░╚═╝░░░░░╚═╝░░╚═╝░╚════╝░╚══════╝

░█████╗░████████╗████████╗░█████╗░██╗░░██╗  ████████╗░█████╗░░█████╗░██╗░░░░░
██╔══██╗╚══██╔══╝╚══██╔══╝██╔══██╗██║░██╔╝  ╚══██╔══╝██╔══██╗██╔══██╗██║░░░░░
███████║░░░██║░░░░░░██║░░░██║░░╚═╝█████═╝░  ░░░██║░░░██║░░██║██║░░██║██║░░░░░
██╔══██║░░░██║░░░░░░██║░░░██║░░██╗██╔═██╗░  ░░░██║░░░██║░░██║██║░░██║██║░░░░░
██║░░██║░░░██║░░░░░░██║░░░╚█████╔╝██║░╚██╗  ░░░██║░░░╚█████╔╝╚█████╔╝███████╗
╚═╝░░╚═╝░░░╚═╝░░░░░░╚═╝░░░░╚════╝░╚═╝░░╚═╝  ░░░╚═╝░░░░╚════╝░░╚════╝░╚══════╝\n"""
    prompt = "SWAT> "

    def default(self, line):
        args = line.split()
        command_name = args[0]

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
        command = command_class(args)
        command.execute()

    def do_exit(self, arg):
        """Exit the shell."""
        print("""
██╗░░░██╗███╗░░██╗████████╗██╗██╗░░░░░  ███╗░░██╗███████╗██╗░░██╗████████╗
██║░░░██║████╗░██║╚══██╔══╝██║██║░░░░░  ████╗░██║██╔════╝╚██╗██╔╝╚══██╔══╝
██║░░░██║██╔██╗██║░░░██║░░░██║██║░░░░░  ██╔██╗██║█████╗░░░╚███╔╝░░░░██║░░░
██║░░░██║██║╚████║░░░██║░░░██║██║░░░░░  ██║╚████║██╔══╝░░░██╔██╗░░░░██║░░░
╚██████╔╝██║░╚███║░░░██║░░░██║███████╗  ██║░╚███║███████╗██╔╝╚██╗░░░██║░░░
░╚═════╝░╚═╝░░╚══╝░░░╚═╝░░░╚═╝╚══════╝  ╚═╝░░╚══╝╚══════╝╚═╝░░╚═╝░░░╚═╝░░░

████████╗██╗███╗░░░███╗███████╗░░░░░░░░░
╚══██╔══╝██║████╗░████║██╔════╝░░░░░░░░░
░░░██║░░░██║██╔████╔██║█████╗░░░░░░░░░░░
░░░██║░░░██║██║╚██╔╝██║██╔══╝░░░░░░░░░░░
░░░██║░░░██║██║░╚═╝░██║███████╗██╗██╗██╗
░░░╚═╝░░░╚═╝╚═╝░░░░░╚═╝╚══════╝╚═╝╚═╝╚═╝""")
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
    SWATShell().cmdloop()