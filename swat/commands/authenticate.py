import argparse
import json
import os
import pickle
from pathlib import Path
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from swat.commands.base_command import BaseCommand
from swat.utils import (ROOT_DIR, validate_args)

DEFAULT_TOKEN_FILE = ROOT_DIR / "token.pickle"
DEFAULT_CRED_FILE = ROOT_DIR / "credentials.json"

class Command(BaseCommand):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.parser = argparse.ArgumentParser(prog='authenticate',
                                            description='SWAT authentication.',
                                            usage='authenticate [options]')
        self.parser.add_argument('--use-service-account', action='store_true',
                                help='Use service account for authentication')
        self.parser.add_argument('--store-token', action='store_true',
                                help='Store the access token for future use')
        self.parser.add_argument("--credentials", default=DEFAULT_CRED_FILE, type=Path,
                                help="Path to the credentials or service account key file")
        self.parser.add_argument("--token", default=DEFAULT_TOKEN_FILE, type=Path,
                                help="Path to the token file")
        self.args = validate_args(self.parser, kwargs.get('args'))

        # Check if environment variables exist for credentials and token files
        self.credentials_file = Path(os.environ.get("SWAT_CREDENTIALS", self.args.credentials if self.args else DEFAULT_CRED_FILE))
        self.token_file = Path(os.environ.get("SWAT_TOKEN", self.args.token if self.args else DEFAULT_TOKEN_FILE))


    def _authenticate_oauth(self) -> Optional[Credentials]:
        """Authenticate with Google Workspace using OAuth2.0."""
        self._check_file_exists(self.credentials_file, f"Missing OAuth2.0 credentials file: {self.credentials_file}")

        creds = None
        if self.token_file.exists():
            creds = pickle.loads(self.token_file.read_bytes())
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                return creds

        flow = InstalledAppFlow.from_client_secrets_file(str(self.credentials_file), self.config['google']['scopes'])
        creds = flow.run_local_server(port=0)

        if self.args.store_token:
            self.token_file.write_bytes(pickle.dumps(creds))

        return creds

    def _authenticate_service_account(self) -> Optional[Credentials]:
        """Authenticate with Google Workspace using a service account."""
        self._check_file_exists(self.credentials_file, f"Missing service account credentials file: {self.credentials_file}")
        creds = ServiceAccountCredentials.from_service_account_file(str(self.credentials_file), scopes=self.config['google']['scopes'])
        return creds

    @staticmethod
    def _check_file_exists(file: Path, error_message: str) -> None:
        """Check if the given file exists, raise an error if it does not."""
        if not file.exists():
            raise FileNotFoundError(error_message)
        if file.is_dir():
            raise IsADirectoryError(error_message)

    def execute(self) -> None:
        self.creds = None
        if self.args is not None:
            if self.args.use_service_account:
                self.creds = self._authenticate_service_account()
            else:
                self.creds = self._authenticate_oauth()
        return self.creds
