import argparse
import json
import os
import pickle
from pathlib import Path
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from ..commands.base_command import BaseCommand
from ..utils import ROOT_DIR
from ..misc import validate_args

DEFAULT_TOKEN_FILE = ROOT_DIR / "token.pickle"
DEFAULT_CRED_FILE = ROOT_DIR / "credentials.json"

def get_default_token_file():
    return DEFAULT_TOKEN_FILE

def get_default_cred_file():
    return DEFAULT_CRED_FILE

class Command(BaseCommand):
    parser = BaseCommand.load_parser(prog='auth',
                                    description='SWAT authentication.')
    parser.add_argument('--use-service-account', action='store_true',
                                help='Use service account for authentication')
    parser.add_argument('--store-token', action='store_true',
                                help='Store the access token for future use')
    parser.add_argument("--credentials", default=DEFAULT_CRED_FILE, type=Path,
                                help="Path to the credentials or service account key file")
    parser.add_argument("--token", default=DEFAULT_TOKEN_FILE, type=Path,
                                help="Path to the token file")
    parser.add_argument("--add-creds", type=str,
                                help="Store the generated credentials with this key")
    parser.add_argument("--remove-creds", type=str,
                                help="Remove stored credentials with this key")
    parser.add_argument("--list-creds", action='store_true',
                                help="List all stored credentials")
    parser.add_argument("--add-scope", type=str,
                                help="Add a scope for the authentication")
    parser.add_argument("--remove-scope", type=str,
                                help="Remove a scope for the authentication")
    parser.add_argument("--list-scopes", action='store_true',
                                help="List all the scopes for the authentication")

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.args = validate_args(self.parser, kwargs.get('args', []))
        self.credentials_file = Path(os.environ.get("SWAT_CREDENTIALS", self.args.credentials if self.args.credentials else DEFAULT_CRED_FILE))
        self.token_file = Path(os.environ.get("SWAT_TOKEN", self.args.token if self.args.token else DEFAULT_TOKEN_FILE))

        if self.obj.CONFIG['google']['scopes'] is not None:
            self.obj.CONFIG['google']['scopes'] = self.obj.CONFIG['google']['scopes']

    def _authenticate_oauth(self) -> Optional[Credentials]:
        """Authenticate with Google Workspace using OAuth2.0."""
        self._check_file_exists(self.credentials_file, f"Missing OAuth2.0 credentials file: {self.credentials_file}")

        creds = None
        if self.token_file.exists():
            creds = pickle.loads(self.token_file.read_bytes())
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                return creds

        flow = InstalledAppFlow.from_client_secrets_file(str(self.credentials_file), self.obj.config['google']['scopes'])
        creds = flow.run_local_server(port=0)

        if self.args.store_token:
            self.token_file.write_bytes(pickle.dumps(creds))

        return creds

    def _authenticate_service_account(self) -> Optional[Credentials]:
        """Authenticate with Google Workspace using a service account."""
        self._check_file_exists(self.credentials_file, f"Missing service account credentials file: {self.credentials_file}")
        creds = Credentials.from_service_account_file(str(self.credentials_file), scopes=self.obj.config['google']['scopes'])
        return creds

    @staticmethod
    def _check_file_exists(file: Path, error_message: str) -> None:
        """Check if the given file exists, raise an error if it does not."""
        if not file.exists():
            raise FileNotFoundError(error_message)
        if file.is_dir():
            raise IsADirectoryError(error_message)

    def execute(self) -> None:
        if self.args is not None:
            # If no specific action is requested, perform authentication
            if not any([self.args.add_creds, self.args.remove_creds, self.args.list_creds, self.args.add_scope, self.args.remove_scope, self.args.list_scopes]):
                self.creds = self._authenticate_service_account() if self.args.use_service_account else self._authenticate_oauth()
                if self.creds:
                    self.obj.creds = self.creds
                    self.logger.info(f"Authenticated successfully.")
                else:
                    self.logger.info(f"Failed to authenticate.")
            # Then continue with the specific actions
            elif self.args.add_creds:
                self.creds = self._authenticate_service_account() if self.args.use_service_account else self._authenticate_oauth()
                if self.creds:
                    self.obj.cred_store.add_creds(self.args.add_creds, self.creds)
                    self.logger.info(f"Credentials added with key: {self.args.add_creds}")
                else:
                    self.logger.info(f"Failed to generate credentials.")
            elif self.args.remove_creds:
                removed = self.obj.cred_store.remove_creds(self.args.remove_creds)
                if removed:
                    self.logger.info(f"Removed credentials with key: {self.args.remove_creds}")
                else:
                    self.logger.info(f"No credentials found with key: {self.args.remove_creds}")
            elif self.args.list_creds:
                cred_keys = self.obj.cred_store.list_creds()
                self.logger.info(f"Stored credentials: {', '.join(cred_keys)}")
            elif self.args.add_scope:
                    self.obj.CONFIG['google']['scopes'].append(self.args.add_scope)
                    self.logger.info(f"Added scope: {self.args.add_scope}")
            elif self.args.remove_scope:
                if self.args.remove_scope in self.obj.CONFIG['google']['scopes']:
                    self.obj.CONFIG['google']['scopes'].remove(self.args.remove_scope)
                    self.logger.info(f"Removed scope: {self.args.remove_scope}")
                else:
                    self.logger.info(f"Scope not found: {self.args.remove_scope}")
            elif self.args.list_scopes:
                self.logger.info(f"OAuth scopes: {', '.join(self.obj.CONFIG['google']['scopes'])}")

