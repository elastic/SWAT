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

import secrets
import string
from typing import Dict, List, Optional

from googleapiclient.discovery import build

from swat.emulations.base_emulation import BaseEmulation


class Emulation(BaseEmulation):
    """
    Emulation class to add privileged roles to a user in Google Workspace.
    Specifically, this class creates a user and assigns admin roles to that user.
    """

    parser = BaseEmulation.load_parser(description='Add privileged roles to a user.')
    parser.add_argument('session_key', default='default', help='Session to use for service building API service')
    parser.add_argument('--username', required=False, help='Username to add the role to, email address format')
    parser.add_argument('--password', required=False, help='Password for the user')
    parser.add_argument('--roles', required=False, help='Roles to add, comma-separated.')
    parser.add_argument('--cleanup', action='store_true', help='Delete the created user after emulation')

    techniques = ['T1098.003']
    name = 'Add Admin Roles to User(s)'
    services = ['admin']
    scopes = ['admin.directory.user', 'admin.directory.rolemanagement']
    description = 'Create a user and assign admin roles to that user.'
    references =['https://developers.google.com/admin-sdk/directory/v1/guides/manage-roles']

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        # session_key is the key used to store the credentials and session in the cred store
        # creds and session should be for the admin user
        self.service = build('admin', 'directory_v1', credentials=self.obj.cred_store.store[self.args.session_key].session)

        # override configuration settings if provided
        if self.args.username:
            self.econfig['user']['primaryEmail'] = kwargs['username']
        if self.args.password:
            self.econfig['user']['password'] = kwargs['password']
        if self.args.roles:
            self.econfig['roles'] = [role.strip() for role in kwargs['roles'].split(',')]

    def generate_password(self, length: int = 12) -> str:
        """Generate a random password."""
        characters = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(secrets.choice(characters) for _ in range(length))
        self.elogger.info(f"Generated password: {password}")
        return password

    def create_user(self) -> Optional[Dict[str, str]]:
        """Create a user in Google Workspace or fetch existing user details using configuration settings."""

        user_info = self.econfig['user']
        user_info['primaryEmail'] = f'{user_info["name"]["givenName"]}-{user_info["name"]["familyName"]}@{self.domain}'
        user_info['password'] = self.generate_password()

        try:
            user = self.service.users().insert(body=user_info).execute()
            self.elogger.info(f"User created: {user['primaryEmail']}")
            return user

        except Exception as e:
            if 'entity already exists' in str(e).lower():  # Check for the specific error
                self.elogger.info(f"already exists: {user_info['primaryEmail']}")

                # Fetch the existing user's details
                user = self.service.users().get(userKey=user_info['primaryEmail']).execute()
                return user

            else:
                self.elogger.error(f"Error creating user: {str(e)}")
                return None


    def get_admin_roles(self) -> List[str]:
        """Get admin roles from Google Workspace."""

        if self.args.roles:
            # override configuration settings if provided via command line
            return self.econfig['roles']
        results = self.service.roles().list(customer='my_customer').execute()
        admin_roles = [role['roleId'] for role in results.get('items', []) if 'admin' in role['roleName'].lower()]
        return admin_roles

    def assign_roles_to_user(self, user: Dict[str, str], roles: List[str]) -> None:
        """Assign roles to the given user using configuration settings."""

        for role in roles:
            try:
                body = {
                    'assignedTo': user['id'],
                    'roleId': role,
                    'scopeType': 'CUSTOMER'
                }
                self.service.roleAssignments().insert(customer='my_customer', body=body).execute()
                self.elogger.info(f"Role {role} added to user {user['primaryEmail']}")
            except Exception as e:
                self.elogger.error(f"Error assigning role {role} to user {user['primaryEmail']}: {str(e)}")

    def cleanup(self, user: Dict[str, str]) -> None:
        """Cleanup function to delete the created user after the emulation."""
        try:
            self.service.users().delete(userKey=user['primaryEmail']).execute()
            self.elogger.info(f"User {user['primaryEmail']} deleted successfully!")
        except Exception as e:
            self.elogger.error(f"Error deleting user: {e}")

    def execute(self) -> None:
        """Execute the emulation."""
        self.elogger.info(self.exec_str(self.parser.description))
        user = self.create_user()
        admin_role_ids = self.get_admin_roles()
        self.assign_roles_to_user(user, admin_role_ids)
        if self.args.cleanup:
            self.cleanup(user)
        self.elogger.info('Emulation complete.')
