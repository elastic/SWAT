from swat.emulations.base_emulation import BaseEmulation
from swat.commands.emulate import AttackData


class Emulation(BaseEmulation):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def execute(self) -> None:
        self.logger.info(f"Executing emulation for {self.tactic}/{self.technique}")
