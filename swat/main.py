
import argparse
import logging
from pathlib import Path

from . import utils
from .logger import configure_logging
from .misc import colorful_exit_message
from .shell import SWATShell


ROOT_DIR = Path(__file__).parent.parent.absolute()
ETC_DIR = ROOT_DIR / 'swat' / 'etc'

DEFAULT_CUSTOM_CONFIG_PATH = ETC_DIR / 'custom_config.yaml'
CONFIG: dict = utils.load_etc_file('config.yaml')


def main():
    parser = argparse.ArgumentParser(description='SWAT CLI')
    parser.add_argument('--debug', action='store_true', help='Debug mode')
    parser.add_argument('--custom-config', type=Path, default=DEFAULT_CUSTOM_CONFIG_PATH,
                        help='Optional custom config file')
    args = parser.parse_args()

    level = logging.DEBUG if args.debug else logging.INFO
    configure_logging(CONFIG, level)

    # Start the interactive shell
    shell = SWATShell(args)

    try:
        shell.cmdloop()
    finally:
        if shell.save_on_exit:
            shell.obj.cred_store.save()
            shell.obj.config.save_custom()
        print(colorful_exit_message())


if __name__ == '__main__':
    main()
