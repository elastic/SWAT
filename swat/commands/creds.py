
from pathlib import Path

from ..base import OAuthCreds, ServiceAccountCreds
from ..commands.base_command import BaseCommand
from ..misc import validate_args


class Command(BaseCommand):
    parser = BaseCommand.load_parser(description='SWAT credential config management.')
    subparsers = parser.add_subparsers(dest='subcommand', title='subcommands', required=True)

    parser_add = subparsers.add_parser('add', description='Load credential config to the cred store',
                                       help='Load credential config to the cred store')
    parser_add.add_argument('key', help='Name of key to store the creds under')
    parser_add.add_argument('config', type=Path, help='Path to the credentials config file')
    parser_add.add_argument('--service-account', action='store_true', help='Service account credential config')
    parser_add.add_argument('--override', action='store_true', help='Override an existing store')

    parser_remove = subparsers.add_parser('remove', description='Remove credential config from the cred store',
                                          help='Remove credential config from the cred store')
    parser_remove.add_argument('key', help='Name of key to remove from the creds store')

    parser_list = subparsers.add_parser('list', description='List credential configs within the cred store',
                                        help='List credential configs within the cred store')

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.parser_add.set_defaults(func=self.add_creds)
        self.parser_remove.set_defaults(func=self.remove_creds)
        self.parser_list.set_defaults(func=self.list_configs)

        self.args = validate_args(self.parser, self.args)

    def add_creds(self):
        assert self.args.config.exists(), f'Credentials config file not found: {self.args.config}'

        try:
            if self.args.service_account:
                config = ServiceAccountCreds.from_file(self.args.config)
            else:
                config = OAuthCreds.from_file(self.args.config) if self.args.config else None

            self.obj.cred_store.add(self.args.key, config=config, override=self.args.override)
            self.logger.info(f'Credentials config added with key: {self.args.key}')
        except TypeError as e:
            self.logger.info(f'Invalid credentials config file: {self.args.config} - {e}')

    def remove_creds(self):
        removed = self.obj.cred_store.remove(self.args.key)
        if removed:
            self.logger.info(f'Removed credentials config with key: {self.args.key}')
        else:
            self.logger.info(f'No credentials config found with key: {self.args.key}')

    def list_configs(self):
        cred_configs = self.obj.cred_store.list_configs()
        self.logger.info(f'Stored credential configs: {", ".join(cred_configs) if cred_configs else None}')

    def execute(self) -> None:
        self.args.func()
