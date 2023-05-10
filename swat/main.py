
import argparse
from pathlib import Path

from . import utils
from .google_auth import authenticate
from .shell import SWATShell


ROOT_DIR = Path(__file__).parent.parent.absolute()
DEFAULT_TOKEN_FILE = ROOT_DIR / "token.pickle"
DEFAULT_CRED_FILE = ROOT_DIR / "credentials.json"
CONFIG: dict = utils.load_etc_file("config.yaml")


def main():
    parser = argparse.ArgumentParser(description="SWAT CLI")
    parser.add_argument("--credentials", default=DEFAULT_CRED_FILE, type=Path, help="Path to the credentials file")
    parser.add_argument("--token", default=DEFAULT_TOKEN_FILE, type=Path, help="Path to the token file")
    args = parser.parse_args()

    # Authenticate with Google Workspace
    scopes = CONFIG['google']['scopes']
    authenticate(scopes, args.credentials.resolve(), args.token.resolve())

    # Start the interactive shell
    SWATShell(args).cmdloop()


if __name__ == '__main__':
    main()
