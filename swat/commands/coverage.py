
import pandas as pd

from ..commands.base_command import BaseCommand
from ..utils import ROOT_DIR
from ..attack import download_attack_data, lookup_technique_by_id
from ..misc import validate_args

EMULATIONS_DIR = ROOT_DIR / 'swat' / 'emulations'
DATAFRAME_COLS = ['id', 'tactic', 'name', 'reference', 'description', 'emulation']


class Command(BaseCommand):

    parser = BaseCommand.load_parser(prog='coverage',
                                     description='SWAT MITRE ATT&CK coverage details.')
    parser.add_argument("--tactic", type=str, help="Tactic to list techniques for.")
    parser.add_argument("--all", action="store_true", help="List all tactics and techniques")
    parser.add_argument("--refresh", action="store_true", help="Refresh the ATT&CK data")

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.args = validate_args(self.parser, self.args)
        self.tactics = self.get_tactics()
        self.coverage = []

    @staticmethod
    def get_tactics():
        """List all available tactics"""
        tactics = [tactic.name for tactic in EMULATIONS_DIR.iterdir() if
                   tactic.is_dir() and not tactic.name.startswith('_') and
                   not tactic.name.endswith('.py')]
        return tactics

    def get_techniques_by_tactic(self, tactic_name) -> dict:
        """List all available techniques for a given tactic."""
        if tactic_name not in self.tactics:
            raise ValueError(f"Tactic {tactic_name} not found.")
        tactic_dir = EMULATIONS_DIR / tactic_name
        techniques = {tactic_name: [f.stem for f in tactic_dir.iterdir()
                      if f.is_file() and not f.name.startswith('__')]}
        return techniques

    def get_all_techniques(self) -> dict:
        """List all available techniques for all available tactics."""
        techniques = {tactic.stem: self.get_techniques_by_tactic(tactic.stem)[tactic.stem]
                      for tactic in EMULATIONS_DIR.iterdir() if tactic.is_dir()
                      and not tactic.name.startswith('_') and not tactic.name.endswith('.py')}
        return techniques

    def get_technique_details(self, technique_id) -> None:
        """Print technique details."""
        if "_" in technique_id:
            technique_id = technique_id.replace("_", ".")
        technique_info = lookup_technique_by_id(f'{technique_id.capitalize()}')
        if technique_info:
            description = technique_info['description'][0: technique_info['description'].find('.') + 1]
            technique_id = technique_info['external_references'][0].get('external_id')
            technique_name = technique_info.get('name')
            tactic_name = technique_info['kill_chain_phases'][0].get('phase_name')
            reference = technique_info['external_references'][0].get('url')
            self.coverage.append({'id': technique_id,
                                  'tactic': tactic_name,
                                  'name': technique_name,
                                  'description': description,
                                  'reference': reference,
                                  'emulation': f'coverage {tactic_name} {technique_id}'})
        else:
            self.logger.info(f"Technique with ID {technique_id} not found.")

    def load_tactics_and_techniques(self, tactics_and_techniques) -> None:
        """Print all tactics and techniques."""
        for tactic, techniques in tactics_and_techniques.items():
            for technique_id in techniques:
                self.get_technique_details(technique_id)

    def execute(self) -> None:
        """Main execution method."""
        if self.args:
            if self.args.refresh:
                self.logger.info("Refreshing ATT&CK data""")
                download_attack_data()
                return
            if self.args.all:
                tactics_and_techniques = self.get_all_techniques()
            elif self.args.tactic:
                tactics_and_techniques = self.get_techniques_by_tactic(self.args.tactic)
            else:
                return
            self.load_tactics_and_techniques(tactics_and_techniques)
            print(pd.DataFrame(self.coverage, columns=DATAFRAME_COLS)
                  .to_markdown(index=False, maxcolwidths=[None, 20], tablefmt="fancy_grid"))
