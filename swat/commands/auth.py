
from pathlib import Path
from typing import Optional

from google.oauth2.service_account import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from ..commands.base_command import BaseCommand
from ..utils import ROOT_DIR, check_file_exists
from ..misc import validate_args

DEFAULT_TOKEN_FILE = ROOT_DIR / 'token.pickle'


class Command(BaseCommand):

    parser = BaseCommand.load_parser(description='Authenticate to google workspace with oauth or service accounts.')
    subparsers = parser.add_subparsers(dest='subcommand', title='subcommands', required=True)

    parser_session = subparsers.add_parser('session', description='Authenticate with Google Workspace (default oauth)',
                                           help='Authenticate with Google Workspace (default oauth)')
    parser_session.add_argument('--default', action='store_true', help='Store the credentials as default')
    parser_session.add_argument('--key', help='Name of key to store the creds under')
    parser_session.add_argument('--config', type=Path, help='Path to the credentials config file')
    parser_session.add_argument('--service-account', action='store_true', help='Authenticate a service account')

    parser_list = subparsers.add_parser('list', description='List credential sessions within the cred store',
                                        help='List credential sessions within the cred store')

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.parser_session.set_defaults(func=self.authenticate)
        self.parser_list.set_defaults(func=self.list_sessions)

        self.args = validate_args(self.parser, self.args)

    def authenticate(self) -> Optional[Credentials]:
        '''Authenticate with Google Workspace using OAuth2.0.'''
        if self.args.key:
            validate_type = 'service' if self.args.service_account else 'oauth'
            cred = self.obj.cred_store.get(self.args.key, validate_type=validate_type)
            self.logger.info(f'Using stored credentials with key: {self.args.key}')

            if cred.session:
                session = cred.refreshed_session()
            else:
                if self.args.service_account:
                    session = Credentials.from_service_acccount_info(cred.config.to_dict())
                else:
                    flow = InstalledAppFlow.from_client_config(cred.config.to_dict(), self.obj.config['google']['scopes'])
                    session = flow.run_local_server(port=0)
                    cred.session = session
        elif self.args.config:
            if self.args.service_account:
                check_file_exists(self.args.config, f'Missing service account credentials file')
                self.logger.info(f'Using service account credentials file: {self.args.config}')
                scopes = self.obj.config['google']['scopes']
                session = Credentials.from_service_account_file(str(self.args.config), scopes=scopes)
            else:
                check_file_exists(self.args.config, f'Missing OAuth2.0 credentials file: {self.args.config}')
                flow = InstalledAppFlow.from_client_secrets_file(str(self.args.config), self.obj.config['google']['scopes'])
                session = flow.run_local_server(port=0)
            if self.args.default:
                self.obj.cred_store.add('default', config=self.args.config, override=True, session=session)
        else:
            self.logger.info(f'Missing key or credentials file.')
            return None

        self.logger.info(f'Authenticated successfully.' if session else f'Failed to authenticate.')
        return session

    def list_sessions(self):
        cred_sessions = self.obj.cred_store.list_sessions()
        self.logger.info(f'Stored credential sessions: {", ".join(cred_sessions) if cred_sessions else None}')

    def execute(self) -> None:
        self.args.func()
