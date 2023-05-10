from swat.commands.base_command import BaseCommand
from swat.commands.emulate import AttackData


class Command(BaseCommand):
    def __init__(self, **kwargs) -> None:
        super().__init__()

    def execute(self, attack: AttackData) -> None:
        self.logger.info(f"Executing emulation for {attack}")
