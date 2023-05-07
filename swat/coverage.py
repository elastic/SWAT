from swat.commands.base_command import BaseCommand
from swat.main import CONFIG_DIR

class Command(BaseCommand):
    def __init__(self, args):
        super().__init__(args)
        self.tactics = yaml.safe_load(open(CONFIG_DIR, "r"))["tactics"]

    def execute(self):
        print("[+] MITRE ATT&CK Coverage")