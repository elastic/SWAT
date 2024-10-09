from pathlib import Path

import yaml
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from swat.commands.base_command import BaseCommand
from swat.commands.emulate import AttackData

class Command(BaseCommand):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def execute(self, attack: AttackData) -> None:
        # https://github.com/elastic/SWAT/issues/5
        self.logger.info(f"Executing emulation for {attack}")

        # Determine the config file name
        current_file = Path(__file__)
        config_file_path = current_file.with_suffix('.yaml')

        # Load user data from the config file
        try:
            with open(config_file_path, "r") as config_file:
                self.config_data = yaml.safe_load(config_file)
        except FileNotFoundError:
            self.log.error(f"Config file '{config_file_path}' not found.")
            return

        if not self._create_user():
            self.log.error(f"User creation failed for {self.config_data['email']}.")
            return

        if self.config_data["cleanup"]:
            self.cleanup()


    def _create_user(self):
        try:
            service = build('admin', 'directory_v1', credentials=self.creds)
            user_info = {
                "name": {
                    "familyName": self.config_data["username"],
                    "givenName": self.config_data["username"],
                },
                "password": self.config_data["password"],
                "primaryEmail": self.config_data["email"],
            }
            service.users().insert(body=user_info).execute()
            self.logger.info(f"User `{self.config_data['email']}` created successfully.")
            return True
        except HttpError as error:
            self.logger.error(f"An error occurred: {error}")
            return False


    def cleanup(self):
        if not self._delete_user(self.self.config_data["email"]):
            self.logger.error(f"User deletion failed for {self.config_data['email']}.")
            return

        self.logger.info(f"User `{self.config_data['email']}` deleted successfully.")


    def _delete_user(self, user_key):
        try:
            service = build('admin', 'directory_v1', credentials=self.creds)
            service.users().delete(userKey=user_key).execute()
            return True
        except HttpError as error:
            self.logger.error(f"An error occurred: {error}")
            return False