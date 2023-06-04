from swat.emulations.base_emulation import BaseEmulation


class Emulation(BaseEmulation):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def execute(self) -> None:
        self.logger.info(f"Executing emulation for {self.tactic}/{self.technique}")
