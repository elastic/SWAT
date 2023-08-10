
from swat.emulations.base_emulation import BaseEmulation


class Emulation(BaseEmulation):

    parser = BaseEmulation.load_parser(description='Adds cloud credentials to a user account.')
    parser.add_argument('--username', required=True, help='Username to create')
    parser.add_argument('--password', required=True, help='Password for user')

    techniques = ['T1098.001']
    name = 'Add Cloud Credentials to User(s)'
    services = ['admin']

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def execute(self) -> None:
        self.elogger.info(self.exec_str(self.parser.description))
        self.elogger.info('Hello, world, from T1098!')
