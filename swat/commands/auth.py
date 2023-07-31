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
from ..utils import ROOT_DIR, check_file_exists
from ..misc import validate_args

DEFAULT_TOKEN_FILE = ROOT_DIR / "token.pickle"
DEFAULT_CRED_FILE = ROOT_DIR / "credentials.json"

import argparse
import json
import os
import pickle
from pathlib import Path
from typing import Optional, List
from dataclasses import dataclass

from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from ..commands.base_command import BaseCommand
from ..utils import ROOT_DIR, check_file_exists
from ..misc import validate_args

DEFAULT_TOKEN_FILE = ROOT_DIR / "token.pickle"
DEFAULT_CRED_FILE = ROOT_DIR / "credentials.json"

@dataclass
class ServiceAccountCreds:
    """Data class for service account credentials."""
    type: str
    project_id: str
    private_key_id: str
    private_key: str
    client_email: str
    client_id: str
    auth_uri: str
    token_uri: str
    auth_provider_x509_cert_url: str
    client_x509_cert_url: str

@dataclass
class OAuthCreds:
    """Data class for OAuth2.0 application credentials."""
    client_id: str
    project_id: str
    auth_uri: str
    token_uri: str
    auth_provider_x509_cert_url: str
    client_secret: str
    redirect_uris: List[str]

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
    parser.add_argument("--add-creds", nargs=2, metavar=('KEY', 'CREDENTIALS_FILE'),
                    help="Store the credentials from the given file with the specified key.")
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
        self.args = validate_args(self.parser, self.args)
        self.credentials_file = Path(os.environ.get("SWAT_CREDENTIALS", self.args.credentials if self.args.credentials else DEFAULT_CRED_FILE))
        self.token_file = Path(os.environ.get("SWAT_TOKEN", self.args.token if self.args.token else DEFAULT_TOKEN_FILE))

        if self.obj.config['google']['scopes'] is not None:
            self.obj.config['google']['scopes'] = self.obj.config['google']['scopes']

    def authenticate_oauth(self, credentials_path: Optional[Path] = None, credentials_key: Optional[str] = None) -> Optional[Credentials]:
        """Authenticate with Google Workspace using OAuth2.0."""
        if credentials_key:
            self.logger.info(f"Using stored credentials with key: {credentials_key}")
            creds = self.obj.cred_store.get_creds(credentials_key)
            if creds:
                return creds

        credentials_file = credentials_path if credentials_path is not None else self.credentials_file
        check_file_exists(credentials_file, f"Missing OAuth2.0 credentials file: {credentials_file}")

        creds = None
        if self.token_file.exists():
            self.logger.info(f"Loading token from file: {self.token_file}")
            creds = pickle.loads(self.token_file.read_bytes())
            if creds and creds.expired and creds.refresh_token:
                self.logger.info(f"Refreshing expired token.")
                creds.refresh(Request())
                return creds

        flow = InstalledAppFlow.from_client_secrets_file(str(credentials_file), self.obj.config['google']['scopes'])
        creds = flow.run_local_server(port=0)

        if self.args.store_token:
            self.logger.info(f"Storing token to file: {self.token_file}")
            self.token_file.write_bytes(pickle.dumps(creds))

        return creds

    def authenticate_service_account(self, credentials_path: Optional[Path] = None, credentials_key: Optional[str] = None) -> Optional[Credentials]:
        """Authenticate with Google Workspace using a service account."""
        if credentials_key:
            self.logger.info(f"Using stored service account credentials with key: {credentials_key}")
            creds = self.obj.cred_store.get_creds(credentials_key)
            if creds:
                return creds

        credentials_file = credentials_path if credentials_path is not None else self.credentials_file
        check_file_exists(credentials_file, f"Missing service account credentials file: {credentials_file}")
        creds = Credentials.from_service_account_file(str(credentials_file), scopes=self.obj.config['google']['scopes'])

        return creds

    def execute(self) -> None:
        if self.args is not None:
            # If no specific action is requested, perform default SWAT authentication
            if not any([self.args.add_creds, self.args.remove_creds, self.args.list_creds, self.args.add_scope, self.args.remove_scope, self.args.list_scopes]):
                self.creds = self.authenticate_service_account() if self.args.use_service_account else self.authenticate_oauth()
                if self.creds:
                    self.obj.creds = self.creds
                    self.logger.info(f"Authenticated successfully.")
                else:
                    self.logger.info(f"Failed to authenticate.")
            # Then continue with the specific actions
            elif self.args.add_creds:
                key, credentials_file = self.args.add_creds
                credentials_path = Path(credentials_file)
                if credentials_path.exists():
                    with open(credentials_path) as f:
                        creds_json = json.load(f)
                    try:
                        if self.args.use_service_account:
                            creds = ServiceAccountCreds(**creds_json)
                        else:
                            creds = OAuthCreds(**creds_json['installed'])

                        self.obj.cred_store.add_creds(key, creds)
                        self.logger.info(f"Credentials added with key: {key}")
                    except TypeError:
                        self.logger.info(f"Invalid credentials file: {credentials_file}")
                else:
                    self.logger.info(f"Credentials file not found: {credentials_file}")
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
                    self.obj.config['google']['scopes'].append(self.args.add_scope)
                    self.logger.info(f"Added scope: {self.args.add_scope}")
            elif self.args.remove_scope:
                if self.args.remove_scope in self.obj.config['google']['scopes']:
                    self.obj.config['google']['scopes'].remove(self.args.remove_scope)
                    self.logger.info(f"Removed scope: {self.args.remove_scope}")
                else:
                    self.logger.info(f"Scope not found: {self.args.remove_scope}")
            elif self.args.list_scopes:
                self.logger.info(f"OAuth scopes: {', '.join(self.obj.config['google']['scopes'])}")
