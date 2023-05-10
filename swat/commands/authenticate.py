import pickle
import logging
import typing
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from swat.commands.base_command import BaseCommand

class Command(BaseCommand):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def execute(self) -> None:
        """Authenticate with Google Workspace."""
        self.logger.info(f"Authenticating with Google Workspace using scopes: {self.config['google']['scopes']}")

        creds = None
        if self.token.exists():
            self.logger.info(f"Loading token file: {self.token}")
            creds = pickle.loads(self.token.read_bytes())
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
        else:
            self.logger.info(f"Token file created: {self.token}")
        if not creds:
            assert self.credentials.exists(), self.logger.error(f"Missing credentials file: {self.credentials}")
            flow = InstalledAppFlow.from_client_secrets_file(str(self.credentials), scopes)
            creds = flow.run_local_server(port=0)

        self.token.write_bytes(pickle.dumps(creds))

        return