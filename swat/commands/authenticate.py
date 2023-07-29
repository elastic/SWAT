import pickle
from pathlib import Path
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from swat.commands.base_command import BaseCommand
from swat.utils import (ROOT_DIR, validate_args)


class Command(BaseCommand):
    """Authenticate against a Google Workspace account."""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def execute(self) -> None:
        """Authenticate with Google Workspace."""
        self.logger.info(f"Authenticating with Google Workspace using scopes: {self.obj.config['google']['scopes']}")

        creds = None
        if self.obj.token_path.exists():
            self.logger.info(f"Loading token file: {self.obj.token_path}")
            creds = pickle.loads(self.obj.token_path.read_bytes())
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                return creds
        else:
            self.logger.info(f"Token file created: {self.obj.token_path}")
        if not creds:
            assert self.obj.cred_path.exists(), self.logger.error(f"Missing credentials file: {self.obj.cred_path}")
            flow = InstalledAppFlow.from_client_secrets_file(
                str(self.obj.cred_path), self.obj.config['google']['scopes'])
            creds = flow.run_local_server(port=0)

        self.obj.token_path.write_bytes(pickle.dumps(creds))
        self.obj.creds = creds

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
