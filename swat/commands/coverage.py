
from tabulate import tabulate

from ..commands.base_command import BaseCommand
from ..commands.emulate import Command as EmulateCommand
from ..attack import download_attack_data, lookup_technique_by_id
from ..misc import validate_args
from ..utils import ROOT_DIR


EMULATIONS_DIR = ROOT_DIR / 'swat' / 'emulations'


class Command(BaseCommand):

    parser = BaseCommand.load_parser(description='SWAT MITRE ATT&CK coverage details.')
    subparsers = parser.add_subparsers(dest='subcommand', title="subcommands", required=True)

    parser_refresh = subparsers.add_parser('refresh', description="Refresh ATT&CK data", help='Refresh the ATT&CK data')

    parser_view = subparsers.add_parser('view', description="Show ATT&CK coverage for existing emulations",
                                        help='Show coverage details')
    parser_view.add_argument("--tactic", nargs="*", help="Filter coverage to the specified tactics.")
    parser_view.add_argument("--technique-id", nargs="*", help="Filter coverage to the specified technique IDs.")

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.parser_refresh.set_defaults(func=self.refresh)
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

    def view(self) -> None:
        """View coverage details."""
        entries = self.build_table_entries()
        if not entries:
            print("No results found.")
        else:
            col_widths = [None, None, None, 50, 20, None]
            print(tabulate(entries, headers="keys", maxcolwidths=col_widths, tablefmt="fancy_grid"))

    def execute(self) -> None:
        """Main execution method."""
        self.args.func()
