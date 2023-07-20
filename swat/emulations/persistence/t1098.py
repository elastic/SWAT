
import argparse

from swat.emulations.base_emulation import BaseEmulation


class Emulation(BaseEmulation):
    def __init__(self, **kwargs) -> None:
        self.parser = argparse.ArgumentParser(prog='T1098',
                                              description='Account Manipulation',
                                              usage='T1098 [options]')
        super().__init__(parser=self.parser, **kwargs)

    def execute(self) -> None:
        self.logger.info(self.exec_str(self.parser.description))
        self.logger.info("Hello, world, from T1098!")
