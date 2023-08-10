
from pathlib import Path
from typing import Optional

from google.oauth2.service_account import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from ..commands.base_command import BaseCommand
from ..utils import ROOT_DIR, check_file_exists
from ..misc import validate_args

DEFAULT_TOKEN_FILE = ROOT_DIR / 'token.pkl'


class Command(BaseCommand):

    parser = BaseCommand.load_parser(description='Authenticate to google workspace with oauth or service accounts.')
    subparsers = parser.add_subparsers(dest='subcommand', title='subcommands', required=True)

    parser_session = subparsers.add_parser('session', description='Authenticate with Google Workspace (default oauth)',
                                           help='Authenticate with Google Workspace (default oauth)')
    parser_session.add_argument('--key', help='Name of key to store the creds under')
    parser_session.add_argument('--creds', type=Path, help='Path to the credentials file')
    parser_session.add_argument('--service-account', action='store_true', help='Authenticate a service account')
    parser_session.add_argument('--store', type=str, help='Add authenticated session to credential store with key')
    parser_list = subparsers.add_parser('list', description='List credential sessions within the cred store',
                                        help='List credential sessions within the cred store')

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.parser_session.set_defaults(func=self.authenticate)
        self.parser_list.set_defaults(func=self.list_sessions)

        self.args = validate_args(self.parser, self.args)

    def authenticate(self) -> Optional[Credentials]:
        """Authenticate with Google Workspace using OAuth2.0."""
        if self.args.key:
            validate_type = 'service' if self.args.service_account else 'oauth'
            cred = self.obj.cred_store.get(self.args.key, validate_type=validate_type)
            self.logger.info(f'Using stored credentials with key: {self.args.key}')

            if cred.session:
                session = cred.refreshed_session()
            else:
                if self.args.service_account:
                    session = Credentials.from_service_account_info(cred.creds.to_dict())
                else:
                    flow = InstalledAppFlow.from_client_config(cred.creds.to_dict(), self.obj.config['google']['scopes'])
                    session = flow.run_local_server(port=0)
                    cred.session = session
        elif self.args.creds:
            if self.args.service_account:
                check_file_exists(self.args.creds, f'Missing service account credentials file')
                self.logger.info(f'Using service account credentials file: {self.args.creds}')
                scopes = self.obj.config['google']['scopes']
                session = Credentials.from_service_account_file(str(self.args.creds), scopes=scopes)
            else:
                check_file_exists(self.args.creds, f'Missing OAuth2.0 credentials file: {self.args.creds}')
                flow = InstalledAppFlow.from_client_secrets_file(str(self.args.creds), self.obj.config['google']['scopes'])
                session = flow.run_local_server(port=0)
        else:
            self.logger.info(f'Missing key or credentials file.')
            return None

        self.logger.info(f'Authenticated successfully.' if session else f'Failed to authenticate.')
        if self.args.store:
            cred_type = 'service' if self.args.service_account else 'oauth'
            self.obj.cred_store.add(self.args.store, creds=self.args.creds, session=session, type=cred_type)
        return session

    @staticmethod
    def get_auth_session(creds: dict, type: str, scopes: list) -> Optional[Credentials]:
        """Get an authenticated session from a credentials dict."""
        assert type in ('oauth', 'service'), f'Invalid type: {type}, expected "oauth" or "service"'
        if type == 'oauth':
            flow = InstalledAppFlow.from_client_config(creds, scopes=scopes)
            return flow.run_local_server(port=0)
        else:
            return Credentials.from_service_account_info(creds)

    def list_sessions(self):
        cred_sessions = self.obj.cred_store.list_sessions()
        self.logger.info(f'Stored auth sessions: {", ".join(cred_sessions) if cred_sessions else None}')

    def execute(self) -> None:
        self.args.func()
