
import dataclasses
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Literal, Union

import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from .utils import ROOT_DIR, PathlibEncoder


DEFAULT_CRED_STORE_FILE = ROOT_DIR / 'swat' / 'etc' / '.cred_store.json'


@dataclass
class BaseCreds:
    '''Based creds class for Google Workspace oauth and service accounts.'''

    def to_dict(self):
        return dataclasses.asdict(self)


@dataclass
class ServiceAccountCreds(BaseCreds):
    '''Data class for service account credentials.'''

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

    @classmethod
    def from_file(cls, file: Path):
        return cls(**json.loads(file.read_text()))


@dataclass
class OAuthCreds(BaseCreds):
    '''Data class for OAuth2.0 application credentials.'''

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


CRED_CONFIG_TYPES = Union[OAuthCreds, ServiceAccountCreds]


@dataclass
class Cred:

    config: Optional[CRED_CONFIG_TYPES]
    session: Optional[Credentials]

    @property
    def client_id(self) -> Optional[str]:
        if self.config and hasattr(self.config, 'client_id'):
            return self.config.client_id

    def refreshed_session(self) -> Optional[Credentials]:
        if self.session and self.session.expired and self.session.refresh_token:
            self.session.refresh(Request())
        return self.session

    def to_dict(self):
        return {k: v for k, v in dataclasses.asdict(self).items() if not k.startswith('_')}


@dataclass
class CredStore:
    '''Credentials store object.'''

    path: Path = field(default=DEFAULT_CRED_STORE_FILE)
    store: dict[str, Cred] = field(default_factory=dict)

    def __post_init__(self):
        if not isinstance(self.path, Path):
            self.path = Path(self.path)

    @property
    def has_sessions(self) -> bool:
        '''Return a boolean indicating if the creds have sessions.'''
        for key, cred in self.store.items():
            if cred.session:
                return True
        return False

    @classmethod
    def from_file(cls, file: Path = DEFAULT_CRED_STORE_FILE) -> Optional['CredStore']:
        if file.exists():
            logging.info(f'Loaded cred store dump from: {file}')
            return cls(**json.loads(file.read_text()))

    def save(self):
        logging.info(f'Saved cred store to {self.path}')
        self.path.write_text(json.dumps(dataclasses.asdict(self), indent=2, sort_keys=True, cls=PathlibEncoder))

    def add(self, key: str, config: Optional[CRED_CONFIG_TYPES] = None, session: Optional[Credentials] = None,
            override: bool = False):
        '''Add a credential to the store.'''
        if key in self.store and not override:
            raise ValueError(f'Value exists for: {key}')
        cred = Cred(config=config, session=session)
        self.store[key] = cred

    def remove(self, key: str) -> bool:
        '''Remove cred by key and type.'''
        return self.store.pop(key, None) is not None

    def get(self, key: str, validate_type: Optional[Literal['oauth', 'service']] = None,
            missing_error: bool = True) -> Optional[Cred]:
        value = self.store.get(key)
        config = value.config
        if validate_type and config:
            if validate_type == 'oauth' and not isinstance(config, OAuthCreds):
                raise ValueError(f'Value for {key} is not OAuthCreds')
            elif validate_type == 'service' and not isinstance(config, ServiceAccountCreds):
                raise ValueError(f'Value for {key} is not ServiceAccountCreds')
            elif validate_type not in ('oauth', 'service'):
                raise ValueError(f'Invalid validate_type: {validate_type}, expected "oauth" or "service"')
        if not config and missing_error:
            raise ValueError(f'Value not found for: {key} in the cred store')
        return value

    def get_by_client_id(self, client_id: str, validate_type: Optional[Literal['oauth', 'service']] = None,
            missing_error: bool = True) -> Optional[CRED_CONFIG_TYPES]:
        '''Get cred by client_id.'''
        for key, value in self.store.items():
            if value.client_id == client_id:
                return self.get(key, validate_type, missing_error)

    def list_configs(self) -> list[str]:
        '''Get the list of configs from the store.'''
        return [f'{k}{f":{v.config.__class__.__name__}" if v.config else ""}' for k, v in self.store.items()]

    def list_sessions(self) -> list[str]:
        '''Get the list of sessions from the store.'''
        return [f'{k}:{v.config.__class__.__name__}' for k, v in self.store.items() if v.session]


@dataclass
class SWAT:
    '''Base object for SWAT.'''

    config: dict
    cred_store: CredStore = field(default_factory=lambda: CredStore.from_file() or CredStore())
