import json
import logging
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from swat.base import Cred, CredStore, OAuthCreds, SWAT, ServiceAccountCreds
from swat.commands.auth import Command as AuthCommand
from swat.commands.creds import Command as CredsCommand
from swat.commands.scopes import Command as ScopesCommand
from swat.shell import SWATShell


OAUTH_CLIENT = {
    'installed': {
        'auth_provider_x509_cert_url': 'https://www.googleapis.com/oauth2/v1/certs',
        'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
        'client_id': 'oauth-client-id.apps.googleusercontent.com',
        'client_secret': 'TEST-NOT-A-SECRET',
        'project_id': 'swat-test',
        'redirect_uris': ['http://localhost'],
        'token_uri': 'https://oauth2.googleapis.com/token',
    }
}

SERVICE_ACCOUNT = {
    'auth_provider_x509_cert_url': 'https://www.googleapis.com/oauth2/v1/certs',
    'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
    'client_email': 'swat-test@swat-test.iam.gserviceaccount.com',
    'client_id': 'sa-client-id',
    'client_x509_cert_url': 'https://www.googleapis.com/robot/v1/metadata/x509/swat-test',
    'private_key_id': 'test-key-id',
    'private_key': '-----BEGIN PRIVATE KEY-----\nTEST-NOT-A-SECRET\n-----END PRIVATE KEY-----\n',
    'project_id': 'swat-test',
    'token_uri': 'https://oauth2.googleapis.com/token',
    'type': 'service_account',
    'universe_domain': 'googleapis.com',
}


def write_json(path, payload):
    path.write_text(json.dumps(payload))
    return path


@pytest.fixture
def oauth_creds(tmp_path):
    return OAuthCreds.from_file(write_json(tmp_path / 'client_secret.json', OAUTH_CLIENT))


@pytest.fixture
def service_creds(tmp_path):
    return ServiceAccountCreds.from_file(write_json(tmp_path / 'service_account.json', SERVICE_ACCOUNT))


@pytest.fixture
def store():
    return CredStore()


class TestCredentialLoading:
    def test_oauth_from_file_reads_installed_client(self, oauth_creds):
        assert oauth_creds.client_id == 'oauth-client-id.apps.googleusercontent.com'
        assert oauth_creds.client_secret == 'TEST-NOT-A-SECRET'
        assert oauth_creds.to_dict()['installed']['client_id'] == oauth_creds.client_id

    def test_service_account_from_file(self, service_creds):
        assert service_creds.type == 'service_account'
        assert service_creds.client_email == 'swat-test@swat-test.iam.gserviceaccount.com'
        assert service_creds.client_id == 'sa-client-id'


class TestCredStoreKeys:
    def test_add_get_and_remove_default_key(self, store, oauth_creds):
        store.add('default', creds=oauth_creds, type='oauth')

        cred = store.get('default', validate_type='oauth')
        assert cred.creds.client_id == oauth_creds.client_id
        assert store.store['default'].session is None

        assert store.remove('default') is True
        assert store.remove('default') is False

    def test_preserves_external_key(self, store, oauth_creds):
        store.add('external', creds=oauth_creds, type='oauth')
        assert 'external' in store.store
        assert store.get('external').client_id == oauth_creds.client_id

    def test_add_without_override_raises(self, store, oauth_creds):
        store.add('default', creds=oauth_creds)
        with pytest.raises(ValueError, match='Value exists for: default'):
            store.add('default', creds=oauth_creds)

    def test_add_with_override_replaces(self, store, oauth_creds, service_creds):
        store.add('default', creds=oauth_creds)
        store.add('default', creds=service_creds, override=True, type='service')
        store.get('default', validate_type='service')

    def test_get_missing_key_raises(self, store):
        with pytest.raises(ValueError, match='Value not found for: missing'):
            store.get('missing')

    def test_validate_type_rejects_mismatch(self, store, oauth_creds):
        store.add('default', creds=oauth_creds)
        with pytest.raises(ValueError, match='is not ServiceAccountCreds'):
            store.get('default', validate_type='service')

    def test_get_by_client_id(self, store, oauth_creds):
        store.add('default', creds=oauth_creds)
        found = store.get_by_client_id(oauth_creds.client_id, validate_type='oauth')
        assert found.client_id == oauth_creds.client_id

    def test_legacy_session_attribute(self, store, oauth_creds):
        session = SimpleNamespace(expired=False, refresh_token=None, client_id='session-client')
        store.add('default', creds=oauth_creds, session=session)
        assert store.store['default'].session is session
        assert store.has_sessions is True

    def test_list_credentials_includes_key(self, store, oauth_creds):
        store.add('default', creds=oauth_creds)
        listed = store.list_credentials()
        assert listed
        assert listed[0].startswith('default')

    def test_clear_session_keeps_credential(self, store, oauth_creds):
        session = SimpleNamespace(expired=False, refresh_token=None, client_id='session-client')
        store.add('default', creds=oauth_creds, session=session)

        assert store.clear_session('default') is True
        assert store.store['default'].session is None
        assert store.get('default', validate_type='oauth').client_id == oauth_creds.client_id
        assert store.clear_session('default') is False
        assert store.clear_session('missing') is False


class TestCredStorePersistence:
    def test_save_and_load_round_trip(self, tmp_path, oauth_creds):
        path = tmp_path / 'cred_store.pkl'
        original = CredStore(path=path)
        original.add('default', creds=oauth_creds, type='oauth')
        original.save()

        loaded = CredStore.from_file(path)
        assert loaded is not None
        assert loaded.get('default', validate_type='oauth').client_id == oauth_creds.client_id

    def test_from_file_missing_returns_none(self, tmp_path):
        assert CredStore.from_file(tmp_path / 'missing.pkl') is None


class TestCredSession:
    def test_client_id_from_oauth_creds(self, oauth_creds):
        assert Cred(creds=oauth_creds, session=None).client_id == oauth_creds.client_id

    def test_refreshed_session_returns_unexpired_session(self, oauth_creds):
        session = MagicMock()
        session.expired = False
        session.refresh_token = 'TEST-NOT-A-SECRET'
        cred = Cred(creds=oauth_creds, session=session)

        assert cred.refreshed_session() is session
        session.refresh.assert_not_called()

    def test_refreshed_session_refreshes_expired_token(self, oauth_creds):
        session = MagicMock()
        session.expired = True
        session.refresh_token = 'TEST-NOT-A-SECRET'
        cred = Cred(creds=oauth_creds, session=session)

        assert cred.refreshed_session() is session
        session.refresh.assert_called_once()


class TestCommandParsers:
    def test_auth_session_and_list_parsers(self):
        obj = SWAT(config={'google': {'scopes': []}}, cred_store=CredStore())
        session = AuthCommand(command='auth', args=['session', '--store-key', 'default'], obj=obj)
        assert session.args.subcommand == 'session'
        assert session.args.store_key == 'default'
        assert session.args.subject is None

        listed = AuthCommand(command='auth', args=['list'], obj=obj)
        assert listed.args.subcommand == 'list'

        status = AuthCommand(command='auth', args=['status', '--key', 'default'], obj=obj)
        assert status.args.subcommand == 'status'
        assert status.args.key == 'default'

        logout = AuthCommand(command='auth', args=['logout'], obj=obj)
        assert logout.args.subcommand == 'logout'
        assert logout.args.key == 'default'

    def test_creds_add_remove_list_parsers(self, tmp_path):
        obj = SWAT(config={'google': {'scopes': []}}, cred_store=CredStore())
        creds_file = write_json(tmp_path / 'client_secret.json', OAUTH_CLIENT)

        added = CredsCommand(command='creds', args=['add', 'default', str(creds_file)], obj=obj)
        assert added.args.subcommand == 'add'
        assert added.args.key == 'default'

        removed = CredsCommand(command='creds', args=['remove', 'default'], obj=obj)
        assert removed.args.subcommand == 'remove'

        listed = CredsCommand(command='creds', args=['list'], obj=obj)
        assert listed.args.subcommand == 'list'

    def test_scopes_add_remove_list_parsers(self):
        obj = SWAT(config={'google': {'scopes': []}}, cred_store=CredStore())
        added = ScopesCommand(command='scopes', args=['add', '--scope', 'admin.directory.user'], obj=obj)
        assert added.args.subcommand == 'add'

        listed = ScopesCommand(command='scopes', args=['list'], obj=obj)
        assert listed.args.subcommand == 'list'

    def test_creds_add_execute_stores_default_key(self, tmp_path):
        obj = SWAT(config={'google': {'scopes': []}}, cred_store=CredStore())
        creds_file = write_json(tmp_path / 'client_secret.json', OAUTH_CLIENT)
        command = CredsCommand(command='creds', args=['add', 'default', str(creds_file)], obj=obj)
        command.execute()
        assert obj.cred_store.get('default', validate_type='oauth').client_id == (
            'oauth-client-id.apps.googleusercontent.com'
        )


class TestAuthStatusAndLogout:
    def test_status_omits_secrets(self, caplog, oauth_creds):
        store = CredStore()
        store.add('default', creds=oauth_creds, session=SimpleNamespace(expired=False, client_id='session-client'))
        obj = SWAT(config={'google': {'scopes': []}}, cred_store=store)

        with caplog.at_level(logging.INFO):
            AuthCommand(command='auth', args=['status'], obj=obj).execute()

        assert 'TEST-NOT-A-SECRET' not in caplog.text
        assert 'default: type=oauth session=active identity=oauth-client-id.apps.googleusercontent.com' in caplog.text

    def test_logout_clears_session_and_keeps_creds(self, oauth_creds):
        store = CredStore()
        store.add(
            'default',
            creds=oauth_creds,
            session=SimpleNamespace(expired=False, refresh_token=None, client_id='session-client'),
        )
        obj = SWAT(config={'google': {'scopes': []}}, cred_store=store)

        AuthCommand(command='auth', args=['logout', 'default'], obj=obj).execute()

        assert obj.cred_store.store['default'].session is None
        assert obj.cred_store.get('default', validate_type='oauth').client_id == oauth_creds.client_id


class TestDomainWideDelegation:
    def test_subject_requires_service_account(self, caplog, oauth_creds):
        store = CredStore()
        store.add('default', creds=oauth_creds)
        obj = SWAT(config={'google': {'scopes': []}}, cred_store=store)

        with caplog.at_level(logging.INFO):
            session = AuthCommand(
                command='auth',
                args=['session', '--key', 'default', '--subject', 'user@example.com'],
                obj=obj,
            ).authenticate()

        assert session is None
        assert 'requires --service-account' in caplog.text

    def test_service_account_session_applies_subject(self, service_creds):
        store = CredStore()
        store.add('default', creds=service_creds)
        obj = SWAT(config={'google': {'scopes': []}}, cred_store=store)
        delegated = MagicMock(name='delegated')
        session = MagicMock(name='session')
        session.with_subject.return_value = delegated

        with patch('swat.commands.auth.Credentials.from_service_account_info', return_value=session):
            result = AuthCommand(
                command='auth',
                args=[
                    'session',
                    '--key', 'default',
                    '--service-account',
                    '--subject', 'user@example.com',
                    '--store-key', 'default',
                ],
                obj=obj,
            ).authenticate()

        session.with_subject.assert_called_once_with('user@example.com')
        assert result is delegated
        assert obj.cred_store.store['default'].session is delegated


class TestShellDiscovery:
    def test_shell_registers_auth_creds_and_scopes(self):
        commands = SWATShell.get_commands()
        assert 'auth' in commands
        assert 'creds' in commands
        assert 'scopes' in commands
        assert 'emulate' in commands
        assert 'audit' in commands
        assert 'coverage' in commands
