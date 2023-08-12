#
# Licensed to Elasticsearch under one or more contributor
# license agreements. See the NOTICE file distributed with
# this work for additional information regarding copyright
# ownership. Elasticsearch licenses this file to you under
# the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#

import argparse
import logging
from pathlib import Path

from . import utils
from .logger import configure_logging
from .misc import colorful_exit_message
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
            shell.obj.cred_store.save()
        print(colorful_exit_message())


if __name__ == '__main__':
    main()
