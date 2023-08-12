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

"""Scope management for Google Workspace authentication."""

from ..commands.base_command import BaseCommand
from ..utils import ROOT_DIR, format_scopes
from ..misc import validate_args

DEFAULT_TOKEN_FILE = ROOT_DIR / "token.pickle"


class Command(BaseCommand):
    parser = BaseCommand.load_parser(description='SWAT credential management.')
    subparsers = parser.add_subparsers(dest='subcommand', title="subcommands", required=True)

    parser_add = subparsers.add_parser('add', description="Add a scope for the authentication",
                                       help='Add a scope for the authentication')
    parser_add.add_argument("--scope", required=True, help="Scope to add for the authentication")

    parser_remove = subparsers.add_parser('remove', description="Remove a scope for the authentication",
                                          help='Remove a scope for the authentication')
    parser_remove.add_argument("--scope", required=True, help="Scope to remove for the authentication")

    parser_list = subparsers.add_parser('list', description="List all the scopes for the authentication",
                                        help='List all the scopes for the authentication')

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.parser_add.set_defaults(func=self.add_scope)
        self.parser_remove.set_defaults(func=self.remove_scope)
        self.parser_list.set_defaults(func=self.list_scopes)

        self.args = validate_args(self.parser, self.args)

    def add_scope(self):
        self.args.scope = format_scopes(self.args.scope)
        if self.args.scope in self.obj.config['google']['scopes']:
            self.logger.info(f"Scope already exists: {self.args.scope}")
            return
        self.obj.config['google']['scopes'].append(self.args.scope)
        self.logger.info(f"Added scope(s): {self.args.scope}")

    def remove_scope(self):
        self.args.scope = format_scopes(self.args.scope)
        if self.args.scope in self.obj.config['google']['scopes']:
            self.obj.config['google']['scopes'].remove(self.args.scope)
            self.logger.info(f"Removed scope: {self.args.scope}")
        else:
            self.logger.info(f"Scope not found: {self.args.scope}")

    def list_scopes(self):
        self.logger.info(f"OAuth scopes: {', '.join(self.obj.config['google']['scopes'])}")

    def execute(self) -> None:
        self.args.func()
