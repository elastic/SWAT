import time
import yaml
from pathlib import Path
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from swat.commands.base_command import BaseCommand
from swat.commands.emulate import AttackData

class Command(BaseCommand):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        with open(Path(__file__).with_suffix('.yaml')) as config_file:
            self.config = yaml.safe_load(config_file)

    def create_group(self, service):
        # Create a new group
        self.logger.info(f"Creating new group '{self.config['role_name']}'.")
        group_info = {
            "email": f"{self.config['role_name']}@dejesusarcheology.com",
            "name": self.config['role_name'],
            "description": "Group created for MITRE ATT&CK T1098.003"
        }
        return service.groups().insert(body=group_info).execute()

    def create_user(self, service):
        # Create a new user
        self.logger.info(f"Creating new user '{self.config['user_info']['primaryEmail']}'.")
        user_info = {
            "name": {
                "familyName": self.config['user_info']['familyName'],
                "givenName": self.config['user_info']['givenName'],
            },
            "password": "secure_password",  # Use a secure password here
            "primaryEmail": self.config['user_info']['primaryEmail'],
        }
        return service.users().insert(body=user_info).execute()

    def add_user_to_group(self, service, user, group):
        # Add user to the group
        self.logger.info(f"Adding user '{self.config['user_info']['primaryEmail']}' to group '{self.config['role_name']}'.")
        member_info = {
            "email": self.config['user_info']['primaryEmail'],
            "role": "MEMBER"
        }
        service.members().insert(groupKey=group['id'], body=member_info).execute()

    def execute(self, attack: AttackData) -> None:
        self.logger.info(f"Executing emulation for {attack}")

        try:
            service = build('admin', 'directory_v1', credentials=self.creds)

            group = self.create_group(service)
            time.sleep(3)  # Wait for the group to be created

            user = self.create_user(service)
            time.sleep(3)  # Wait for the user to be created

            self.add_user_to_group(service, user, group)
            time.sleep(3)  # Wait for the user to be added to the group

            if self.config["cleanup"]:
                self.cleanup()

        except HttpError as error:
            self.logger.error(f"An error occurred: {error}")

    def cleanup(self):
        try:
            service = build('admin', 'directory_v1', credentials=self.creds)

            # Remove the user from the group
            self.logger.info(f"Removing user '{self.config['user_info']['primaryEmail']}' from group '{self.config['role_name']}'.")
            service.members().delete(groupKey=f"{self.config['role_name']}domain.com", memberKey=self.config['user_info']['primaryEmail']).execute()
            time.sleep(3)  # Wait for the user to be removed

            # Delete the user
            service.users().delete(userKey=self.config['user_info']['primaryEmail']).execute()
            time.sleep(3)  # Wait for the user to be deleted

            # Delete the group
            self.logger.info(f"Deleting group '{self.config['role_name']}'.")
            service.groups().delete(groupKey=f"{self.config['role_name']}@dejesusarcheology.com").execute()
        except HttpError as error:
            self.logger.error(f"An error occurred: {error}")
