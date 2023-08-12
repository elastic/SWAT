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

"""Coverage support."""

from tabulate import tabulate

from ..commands.base_command import BaseCommand
from ..commands.emulate import Command as EmulateCommand
from ..attack import download_attack_data, load_attack_data
from ..misc import validate_args
from ..utils import ROOT_DIR


EMULATIONS_DIR = ROOT_DIR / 'swat' / 'emulations'


class Command(BaseCommand):

    parser = BaseCommand.load_parser(description='SWAT MITRE ATT&CK coverage details.')
    subparsers = parser.add_subparsers(dest='subcommand', title='subcommands', required=True)

    parser_refresh = subparsers.add_parser('refresh', description='Refresh ATT&CK data', help='Refresh the ATT&CK data')

    parser_version = subparsers.add_parser('version', description='Show ATT&CK version', help='Show ATT&CK version')

    parser_view = subparsers.add_parser('view', description='Show ATT&CK coverage for existing emulations',
                                        help='Show coverage details')
    parser_view.add_argument('--tactic', nargs='*', help='Filter coverage to the specified tactics.')
    parser_view.add_argument('--technique-id', nargs='*', help='Filter coverage to the specified technique IDs.')

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.parser_refresh.set_defaults(func=self.refresh)
        self.parser_version.set_defaults(func=self.version)
        self.parser_view.set_defaults(func=self.view)

        self.args = validate_args(self.parser, self.args)
        self.emulate_commands = EmulateCommand.load_all_emulation_classes()

    def build_table_entries(self) -> list[dict]:
        """Build dict format for table."""
        details = []
        for command in self.emulate_commands:
            details.extend([v for k, v in command.get_attack().technique_details().items()])
        if self.args.tactic:
            details = [d for d in details if d['tactic'] in self.args.tactic]
        if self.args.technique_id:
            details = [d for d in details if d['id'] in self.args.technique_id]
        return details

    @staticmethod
    def refresh() -> None:
        """Refresh the ATT&CK data."""
        download_attack_data()

    def version(self) -> None:
        """Show the ATT&CK version."""
        self.logger.info(f'ATT&CK version: {load_attack_data()["version"]}')

    def view(self) -> None:
        """View coverage details."""
        entries = self.build_table_entries()
        if not entries:
            self.logger.info('No results found.')
        else:
            col_widths = [None, None, None, 30, None, 30]
            print(tabulate(entries, headers='keys', maxcolwidths=col_widths, tablefmt='fancy_grid'))

    def execute(self) -> None:
        """Main execution method."""
        self.args.func()
