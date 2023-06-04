
import argparse
from pathlib import Path

from . import utils
from .shell import SWATShell
from .logger import configure_logging


ROOT_DIR = Path(__file__).parent.parent.absolute()
DEFAULT_TOKEN_FILE = ROOT_DIR / "token.pickle"
DEFAULT_CRED_FILE = ROOT_DIR / "credentials.json"
CONFIG: dict = utils.load_etc_file("config.yaml")


def main():
    configure_logging(CONFIG)
    parser = argparse.ArgumentParser(description="SWAT CLI")
    parser.add_argument("--credentials", default=DEFAULT_CRED_FILE, type=Path, help="Path to the credentials file")
    parser.add_argument("--token", default=DEFAULT_TOKEN_FILE, type=Path, help="Path to the token file")
    args = parser.parse_args()

    # Start the interactive shell
    SWATShell(args).cmdloop()


if __name__ == "__main__":
    main()
