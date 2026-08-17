from swat.base import DEFAULT_CRED_STORE_FILE, CredStore, SWAT
from swat.commands.coverage import Command as CoverageCommand
from swat.commands.emulate import Command as EmulateCommand
from swat.emulations.base_emulation import BaseEmulation
from swat.utils import load_etc_file


KNOWN_COMMANDS = {'audit', 'auth', 'coverage', 'creds', 'emulate', 'scopes'}

KNOWN_EMULATIONS = {
    'admin_add_admin_roles_to_users',
    'admin_add_creds_to_users',
    'admin_disable_2sv_for_user',
    'drive_access_private_keys',
    'gmail_html_with_embedded_js',
    'gmail_phishing_form_link',
}


class TestPublicImports:
    def test_runtime_entry_points_remain_importable(self):
        from swat.base import Cred, CredStore, OAuthCreds, ServiceAccountCreds
        from swat.commands.auth import Command as AuthCommand
        from swat.commands.base_command import BaseCommand
        from swat.commands.creds import Command as CredsCommand
        from swat.main import main
        from swat.shell import SWATShell

        assert CredStore is not None
        assert Cred is not None
        assert OAuthCreds is not None
        assert ServiceAccountCreds is not None
        assert BaseCommand is not None
        assert BaseEmulation is not None
        assert AuthCommand is not None
        assert CredsCommand is not None
        assert callable(main)
        assert SWATShell is not None

    def test_console_script_still_points_at_main(self):
        from pathlib import Path

        pyproject = Path('pyproject.toml').read_text()
        assert "swat = 'swat.main:main'" in pyproject


class TestCommandSurface:
    def test_shell_still_discovers_existing_commands(self):
        from swat.shell import SWATShell

        assert KNOWN_COMMANDS.issubset(set(SWATShell.get_commands()))

    def test_coverage_parser_keeps_existing_subcommands(self):
        obj = SWAT(config={'google': {'scopes': []}}, cred_store=CredStore())
        refresh = CoverageCommand(command='coverage', args=['refresh'], obj=obj)
        version = CoverageCommand(command='coverage', args=['version'], obj=obj)
        view = CoverageCommand(command='coverage', args=['view'], obj=obj)

        assert refresh.args.subcommand == 'refresh'
        assert version.args.subcommand == 'version'
        assert view.args.subcommand == 'view'


class TestEmulationSurface:
    def test_emulation_module_names_remain(self):
        assert KNOWN_EMULATIONS.issubset(set(EmulateCommand.get_emulate_commands()))

    def test_emulations_keep_session_key_and_store_access(self):
        for emulation in EmulateCommand.load_all_emulation_classes():
            dests = {action.dest for action in emulation.parser._actions}
            assert 'session_key' in dests, f'{emulation.name} dropped session_key'
            assert issubclass(emulation, BaseEmulation)


class TestConfigContract:
    def test_default_cred_store_path_stays_repo_local(self):
        assert DEFAULT_CRED_STORE_FILE.name == '.cred_store.pkl'
        assert 'swat' in DEFAULT_CRED_STORE_FILE.parts
        assert 'etc' in DEFAULT_CRED_STORE_FILE.parts

    def test_config_yaml_keeps_operator_settings(self):
        config = load_etc_file('config.yaml')
        assert 'google' in config
        assert 'scopes' in config['google']
        assert 'domain' in config['google']
        assert config['settings']['save_on_exit'] is True
