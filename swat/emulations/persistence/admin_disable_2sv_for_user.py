from typing import Dict, List, Optional
from swat.utils import generate_password
from googleapiclient.discovery import build

from swat.emulations.base_emulation import BaseEmulation


class Emulation(BaseEmulation):
    """
    Emulation class to manage 2SV for a user in Google Workspace.
    Specifically, this class creates a user, enables 2SV if disabled and then disables 2SV.
    Groups and roles can also be added to the user for additional detection opportunities.
    """

    parser = BaseEmulation.load_parser(description='Disable 2SV for a user.')
    parser.add_argument('session_key', default='default', help='Session to use for service building API service')
    parser.add_argument('--username', required=False, help='Username to manage 2SV for, email address format')
    parser.add_argument('--password', required=False, help='Password for the user')
    parser.add_argument('--groups', required=False, nargs='+', help='Groups to add the user to, space-separated.')
    parser.add_argument('--role', required=False, help='Role to assign to the user')
    parser.add_argument('--cleanup', action='store_true', help='Revert changes after emulation')

    techniques = ['T1556.006']
    name = 'Disable 2SV for a User'
    services = ['admin']
    scopes = ['admin.directory.user', 'admin.directory.rolemanagement', 'admin.directory.user.security']
    description = 'Create a user, enable 2SV, add the user to groups, and assign a role.'
    references =['https://developers.google.com/admin-sdk/directory/v1/guides/manage-roles']

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.service = build('admin', 'directory_v1', credentials=self.obj.cred_store.store[self.args.session_key].session)

        if self.args.username:
            self.econfig['user']['primaryEmail'] = kwargs['username']
        if self.args.password:
            self.econfig['user']['password'] = kwargs['password']
        if self.args.groups:
            self.econfig['groups'] = kwargs['groups']
        if self.args.role:
            self.econfig['role'] = kwargs['role']

    def add_user_to_groups(self, user: Dict[str, str], group_ids: List[str]) -> None:
        """Add the specified user to the specified groups."""
        for group_id in group_ids:
            try:
                body = {
                    'email': user['primaryEmail']
                }
                self.service.members().insert(groupKey=group_id, body=body).execute()
                self.elogger.info(f"User {user['primaryEmail']} added to group {group_id}")
            except Exception as e:
                self.elogger.error(f"Error adding user {user['primaryEmail']} to group {group_id}: {str(e)}")

    def assign_role_to_user(self, user: Dict[str, str], role_id: str) -> None:
        """Assign the specified role to the user."""
        try:
            body = {
                'assignedTo': user['id'],
                'roleId': role_id,
                'scopeType': 'CUSTOMER'
            }
            self.service.roleAssignments().insert(customer='my_customer', body=body).execute()
            self.elogger.info(f"Role {role_id} assigned to user {user['primaryEmail']}")
        except Exception as e:
            self.elogger.error(f"Error assigning role {role_id} to user {user['primaryEmail']}: {str(e)}")

    def cleanup(self, user: Dict[str, str]) -> None:
        """Cleanup function."""
        if self.args.groups:
            for group_id in self.args.groups:
                # Assuming you have a method to remove the user from the group
                self.remove_user_from_group(user, group_id)
        if self.args.role:
            # Assuming you have a method to remove the role from the user
            self.remove_role_from_user(user, self.args.role)
        # Delete user (optional, based on your needs)
        try:
            self.service.users().delete(userKey=user['primaryEmail']).execute()
            self.elogger.info(f"User {user['primaryEmail']} deleted successfully!")
        except Exception as e:
            self.elogger.error(f"Error deleting user: {e}")

    def create_user(self) -> Optional[Dict[str, str]]:
        """Create a user in Google Workspace or fetch existing user details using configuration settings."""

        user_info = self.econfig['user']
        user_info['primaryEmail'] = f'{user_info["name"]["givenName"]}-{user_info["name"]["familyName"]}@{self.domain}'
        user_info['password'] = generate_password()
        self.elogger.info(f"User password: {user_info['password']}")

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

    def remove_user_from_group(self, user: Dict[str, str], group_id: str) -> None:
        """Remove the specified user from the specified group."""
        try:
            self.service.members().delete(groupKey=group_id, memberKey=user['primaryEmail']).execute()
            self.elogger.info(f"User {user['primaryEmail']} removed from group {group_id}")
        except Exception as e:
            self.elogger.error(f"Error removing user {user['primaryEmail']} from group {group_id}: {str(e)}")

    def remove_role_from_user(self, user: Dict[str, str], role_id: str) -> None:
        """Remove the specified role from the user."""
        try:
            # Fetch role assignment ID
            assignments = self.service.roleAssignments().list(customer='my_customer', userKey=user['primaryEmail']).execute()
            assignment_id = None
            for assignment in assignments.get('items', []):
                if assignment['roleId'] == role_id:
                    assignment_id = assignment['id']
                    break

            if not assignment_id:
                raise ValueError(f"No assignment found for role {role_id} for user {user['primaryEmail']}")

            # Remove the role
            self.service.roleAssignments().delete(customer='my_customer', assignmentId=assignment_id).execute()
            self.elogger.info(f"Role {role_id} removed from user {user['primaryEmail']}")
        except Exception as e:
            self.elogger.error(f"Error removing role {role_id} from user {user['primaryEmail']}: {str(e)}")

    def execute(self) -> None:
        """Execute the emulation."""
        self.elogger.info(self.exec_str(self.parser.description))
        user = self.create_user()
        self.add_user_to_groups(user, self.econfig.get('groups', []))
        if 'role' in self.econfig:
            self.assign_role_to_user(user, self.econfig['role'])
        if self.args.cleanup:
            self.cleanup(user)
        self.elogger.info('Emulation complete.')