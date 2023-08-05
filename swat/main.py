import argparse
import logging
from pathlib import Path
from . import utils
from .logger import configure_logging
from .shell import SWATShell

ROOT_DIR = Path(__file__).parent.parent.absolute()
CONFIG: dict = utils.load_etc_file('config.yaml')

def main():
    parser = argparse.ArgumentParser(description='SWAT CLI')
    parser.add_argument('--debug', action='store_true', help='Debug mode')
    args = parser.parse_args()

    level = logging.DEBUG if args.debug else logging.INFO
    configure_logging(CONFIG, level)

    # Start the interactive shell
    shell = SWATShell(args)

    try:
        shell.cmdloop()
    finally:
        if shell.save_on_exit:
            pass
            # TODO: resolve object loading on this
            # shell.obj.cred_store.save()


if __name__ == '__main__':
    main()
