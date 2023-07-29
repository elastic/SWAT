
import argparse

from swat.emulations.base_emulation import BaseEmulation


class Emulation(BaseEmulation):

    parser = BaseEmulation.load_parser(prog='T1098',
                                       description='Account Manipulation')

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def execute(self) -> None:
        self.logger.info(self.exec_str(self.parser.description))
        self.logger.info("Hello, world, from T1098!")
