
from swat.emulations.base_emulation import BaseEmulation


class Emulation(BaseEmulation):

    parser = BaseEmulation.load_parser(description='Add privileged roles to a user.')
    parser.add_argument('session_key', default='default', help='Session to use for service building API service')
    parser.add_argument('--username', required=True, help='Username to add the role to')
    parser.add_argument('--roles', required=True, help='Roles to add')

    techniques = ['T1098.003']
    name = 'Add Roles to User(s)'
    services = ['admin']
    scopes = ['admin.directory.user']

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def execute(self) -> None:
        self.elogger.info(self.exec_str(self.parser.description))
        self.elogger.info('Hello, world, from T1098!')