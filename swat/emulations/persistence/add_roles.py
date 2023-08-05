
from swat.emulations.base_emulation import BaseEmulation


class Emulation(BaseEmulation):

    parser = BaseEmulation.load_parser(description='Account Manipulation: Additional Cloud Roles')
    parser.add_argument('--username', required=True, help='Username to add the role to')
    parser.add_argument('--roles', required=True, help='Roles to add')

    techniques = ["T1098.003"]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def execute(self) -> None:
        self.elogger.info(self.exec_str(self.parser.description))
        self.elogger.info("Hello, world, from T1098!")
