#
# Licensed to Elasticsearch under one or more contributor
# license agreements. See the NOTICE file distributed with
# this work for additional information regarding copyright
# ownership. Elasticsearch licenses this file to you under
# the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#

"""Credentials management."""

from pathlib import Path

from ..base import OAuthCreds, ServiceAccountCreds
from ..commands.base_command import BaseCommand
from ..misc import validate_args


class Command(BaseCommand):
    parser = BaseCommand.load_parser(description='SWAT credentials management.')
    subparsers = parser.add_subparsers(dest='subcommand', title='subcommands', required=True)

    parser_add = subparsers.add_parser('add', description='Add credentials to the cred store',
                                       help='Add credentials to the cred store')
    parser_add.add_argument('key', help='Name of key to store the creds under')
    parser_add.add_argument('creds', type=Path, help='Path to the credentials file')
    parser_add.add_argument('--service-account', action='store_true', help='Service account credentials')
    parser_add.add_argument('--override', action='store_true', help='Override an existing store')

    parser_remove = subparsers.add_parser('remove', description='Remove credentials from the cred store',
                                          help='Remove credentials from the cred store')
    parser_remove.add_argument('key', help='Name of key to remove from the creds store')

    parser_list = subparsers.add_parser('list', description='List credentials within the cred store',
                                        help='List credentials within the cred store')

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.parser_add.set_defaults(func=self.add_creds)
        self.parser_remove.set_defaults(func=self.remove_creds)
        self.parser_list.set_defaults(func=self.list_credentials)

        self.args = validate_args(self.parser, self.args)

    def add_creds(self):
        assert self.args.creds.exists(), f'Credentials file not found: {self.args.creds}'

        try:
            if self.args.service_account:
                creds = ServiceAccountCreds.from_file(self.args.creds)
            else:
                creds = OAuthCreds.from_file(self.args.creds) if self.args.creds else None

            self.obj.cred_store.add(self.args.key, creds=creds, override=self.args.override)
            self.logger.info(f'Credentials added with key: {self.args.key}')
        except TypeError as e:
            self.logger.info(f'Invalid credentials file: {self.args.creds} - {e}')

    def remove_creds(self):
        removed = self.obj.cred_store.remove(self.args.key)
        if removed:
            self.logger.info(f'Removed credentials with key: {self.args.key}')
        else:
            self.logger.info(f'No credentials found with key: {self.args.key}')

    def list_credentials(self):
        creds = self.obj.cred_store.list_credentials()
        self.logger.info(f'Stored credentials: {", ".join(creds) if creds else None}')

    def execute(self) -> None:
        self.args.func()
