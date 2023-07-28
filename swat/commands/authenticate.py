
import pickle

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

from swat.commands.base_command import BaseCommand


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
