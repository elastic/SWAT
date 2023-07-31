from typing import Dict, Optional, Any, List
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from google.oauth2.credentials import Credentials

from .misc import default_config


@dataclass
class SWAT:
    """Base object for SWAT."""

    @dataclass
    class CredStore:
        """Credentials store object."""

        cred_store: Dict[str, Any] = field(default_factory=dict)

        def add_creds(self, key: str, value: Any) -> None:
            """Add a credential to the store."""
            self.cred_store[key] = value

        def remove_creds(self, key: str) -> bool:
            """Remove credentials from the store."""
            if key in self.cred_store:
                del self.cred_store[key]
                return True
            return False

        def list_creds(self) -> List[str]:
            """List all stored credentials."""
            return list(self.cred_store.keys())

        def get_creds(self, key: str) -> Optional[Any]:
            """Get specific credentials."""
            return self.cred_store.get(key, None)

    config: dict
    cred_path: Path
    token_path: Path
    creds: Optional[Credentials] = field(default=None)
    cred_store: Optional[CredStore] = field(default_factory=CredStore)

    def add_cred(self, key, value):
        """Add a credential to the store."""
        setattr(self.cred_store, key, value)

    def remove_cred(self, key):
        """Remove a credential from the store."""
        delattr(self.cred_store, key)

    def get_creds(self) -> dict:
        """Get the credentials from the store."""
        return self.cred_store.__dict__
