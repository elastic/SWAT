from typing import Dict, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path

from google.oauth2.credentials import Credentials

from . import utils
import yaml


def default_config():
    with open('swat/etc/config.yaml', 'r') as file:
        return yaml.safe_load(file)


@dataclass
class SWAT:
    """Base object for SWAT."""

    @dataclass
    class CredStore:
        """Credentials store object."""
        creds: Dict[str, Any] = field(default_factory=dict)  # Dict to hold the credentials

        def add_creds(self, key, value):
            """Add a credential to the store."""
            self.creds[key] = value

        def remove_creds(self, key):
            """Remove credentials from the store."""
            if key in self.creds:
                del self.creds[key]
                return True
            return False

        def list_creds(self):
            """List all stored credentials."""
            return list(self.creds.keys())

    config: dict
    cred_path: Path
    token_path: Path
    creds: Optional[Credentials] = field(default=None)
    cred_store: CredStore = field(default_factory=CredStore)
    CONFIG: Dict = field(default_factory=default_config)

