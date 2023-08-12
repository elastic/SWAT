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

from swat.emulations.base_emulation import BaseEmulation


class Emulation(BaseEmulation):

    parser = BaseEmulation.load_parser(description='Add privileged roles to a user.')
    parser.add_argument('session_key', default='default', help='Session to use for service building API service')
    parser.add_argument('--username', required=True, help='Username to add the role to')
    parser.add_argument('--roles', required=True, help='Roles to add')

    techniques = ['T1098.003']
    name = 'Add Roles to User(s)'
    services = ['admin']
    scopes = ['admin.directory.user']

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def execute(self) -> None:
        self.elogger.info(self.exec_str(self.parser.description))
        self.elogger.info('Hello, world, from T1098!')
