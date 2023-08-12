
import copy
import dataclasses
import logging
import pickle
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Literal, Union

from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials as ServiceCredentials
from google.oauth2.credentials import Credentials

import json
import yaml

from .utils import ROOT_DIR, deep_merge


DEFAULT_CRED_STORE_FILE = ROOT_DIR / 'swat' / 'etc' / '.cred_store.pkl'
DEFAULT_EMULATION_ARTIFACTS_DIR = ROOT_DIR / 'swat' / 'etc' / 'artifacts'
DEFAULT_CUSTOM_CONFIG_PATH = ROOT_DIR / 'swat' / 'etc' / 'custom_config.yaml'


@dataclass
class BaseCreds:
    """Based creds class for Google Workspace oauth and service accounts."""

    def to_dict(self):
        return dataclasses.asdict(self)


@dataclass
class ServiceAccountCreds(BaseCreds):
    """Data class for service account credentials."""

    auth_provider_x509_cert_url: str
    auth_uri: str
    client_email: str
    client_id: str
    client_x509_cert_url: str
    private_key_id: str
    private_key: str
    project_id: str
    token_uri: str
    type: str
    universe_domain: str

    @classmethod
    def from_file(cls, file: Path):
        return cls(**json.loads(file.read_text()))


@dataclass
class OAuthCreds(BaseCreds):
    """Data class for OAuth2.0 application credentials."""

    auth_provider_x509_cert_url: str
    auth_uri: str
    client_id: str
    client_secret: str
    project_id: str
    redirect_uris: list[str]
    token_uri: str

    @classmethod
    def from_file(cls, file: Path):
        return cls(**json.loads(file.read_text())['installed'])

    def to_dict(self):
        return {'installed': {k: v for k, v in super().to_dict().items() if not k.startswith('_')}}


CRED_TYPES = Union[OAuthCreds, ServiceAccountCreds]


@dataclass
class Cred:

    creds: Optional[CRED_TYPES]

    def session(self, scopes: Optional[list[str]] = None) -> Optional[Credentials]:
        if isinstance(self.creds, OAuthCreds):
            session = Credentials.from_authorized_user_info(str(self.creds.to_dict()), scopes=scopes)
        else:
            session = ServiceCredentials.from_service_account_info(self.creds.to_dict(), scopes=scopes)

        if session.expired and session.refresh_token:
            session.refresh(Request())
        return session

    @property
    def client_id(self) -> Optional[str]:
        if self.creds and hasattr(self.creds, 'client_id'):
            return self.creds.client_id

    def to_dict(self):
        return {k: v for k, v in dataclasses.asdict(self).items() if not k.startswith('_')}


@dataclass
class CredStore:
    """Credentials store object."""

    path: Path = field(default=DEFAULT_CRED_STORE_FILE)
    store: dict[str, Cred] = field(default_factory=dict)

    def __post_init__(self):
        if not isinstance(self.path, Path):
            self.path = Path(self.path)

    @classmethod
    def from_file(cls, file: Path = DEFAULT_CRED_STORE_FILE) -> Optional['CredStore']:
        if file.exists():
            logging.info(f'Loaded cred store dump from: {file}')
            return pickle.loads(file.read_bytes())

    def save(self):
        logging.info(f'Saved cred store to {self.path}')
        self.path.write_bytes(pickle.dumps(self))

    def add(self, key: str, creds: Optional[CRED_TYPES] = None, override: bool = False,
            cred_type: Optional[Literal["oauth", "service"]] = None):
        """Add a credential to the store."""
        if key in self.store and not override:
            raise ValueError(f'Value exists for: {key}')

        cred = Cred(creds=creds)
        self.store[key] = cred
        logging.info(f'Added {cred_type} cred with key: {key}')

    def remove(self, key: str) -> bool:
        """Remove cred by key and type."""
        return self.store.pop(key, None) is not None

    def get(self, key: str, validate_type: Optional[Literal["oauth", "service"]] = None,
            missing_error: bool = True) -> Optional[Cred]:
        value = self.store.get(key)
        creds = value.creds
        if validate_type and creds:
            if validate_type == 'oauth' and not isinstance(creds, OAuthCreds):
                raise ValueError(f'Value for {key} is not OAuthCreds')
            elif validate_type == 'service' and not isinstance(creds, ServiceAccountCreds):
                raise ValueError(f'Value for {key} is not ServiceAccountCreds')
            elif validate_type not in ('oauth', 'service'):
                raise ValueError(f'Invalid validate_type: {validate_type}, expected "oauth" or "service"')
        if not creds and missing_error:
            raise ValueError(f'Value not found for: {key} in the cred store')
        return value

    def get_by_client_id(self, client_id: str, validate_type: Optional[Literal['oauth', 'service']] = None,
            missing_error: bool = True) -> Optional[CRED_TYPES]:
        """Get cred by client_id."""
        for key, value in self.store.items():
            if value.client_id == client_id:
                return self.get(key, validate_type, missing_error)

    def list_credentials(self) -> list[str]:
        """Get the list of creds from the store."""
        return [f'{k}:{v.creds.__class__.__name__}:{v.creds.project_id}' for k, v in self.store.items()]


class Config:
    """Config class for handling config and custom_config."""

    def __init__(self, path: Path, custom_path: Optional[Path] = DEFAULT_CUSTOM_CONFIG_PATH):
        self.path = path
        self.custom_path = custom_path

        assert path.exists(), f'Config file not found: {path}'
        self.config = yaml.safe_load(path.read_text())

        self.custom_config = yaml.safe_load(custom_path.read_text()) if custom_path.exists() else {}

    @property
    def merged(self) -> dict:
        """Safely retrieve a fresh merge of primary and custom configs."""
        # I regret nothing
        config = copy.deepcopy(self.config)
        return deep_merge(config, self.custom_config)

    def save_custom(self):
        self.custom_path.write_text(yaml.dump(self.custom_config))


@dataclass
class SWAT:
    """Base object for SWAT."""

    config: Config
    cred_store: CredStore = field(default_factory=lambda: CredStore.from_file() or CredStore())
