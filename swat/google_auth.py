import os
import pickle
import typing
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


def authenticate(scopes: list, credentials_file: Path, token_file: Path) -> Credentials:
    creds = None
    if token_file.exists():
        creds = pickle.loads(token_file.read_bytes())
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
    else:
        print(f"token file created: {token_file}")
    if not creds:
        assert credentials_file.exists(), f"Missing credentials file: {credentials_file}"
        flow = InstalledAppFlow.from_client_secrets_file(str(credentials_file), scopes)
        creds = flow.run_local_server(port=0)

    token_file.write_bytes(pickle.dumps(creds))

    return creds
