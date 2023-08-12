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

import base64
import io
# from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from googleapiclient.discovery import build

from swat.emulations.base_emulation import BaseEmulation


class Emulation(BaseEmulation):
    parser = BaseEmulation.load_parser(description='Sends a phishing email to a user with a HTML attachment.')
    parser.add_argument('session_key', default='default', help='Session to use for service building API service')
    parser.add_argument('--recipient', required=True, help='Recipient email address')
    parser.add_argument('--sender', required=True, help='Sender email address')
    parser.add_argument('--subject', default='Phishing Test Email', help='Email subject')
    parser.add_argument('--attachment', default='swat_malicious', help='Attachment name')

    techniques = ['T1566.001', 'T1204.002']
    name = 'Send HTML with Embedded Javascript with Gmail'
    scopes = ['gmail.send','gmail.readonly','gmail.compose']
    services = ['gmail']

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.service = build('gmail', 'v1', credentials=self.obj.cred_store.store[self.args.session_key].session)

    def create_html(self) -> io.BytesIO:
        """Create an HTML file with embedded javascript."""
        js = '<script>alert("Embedded JavaScript by SWAT!");</script>'
        html_content = f'<html><head></head><body>{js}</body></html>'
        return io.BytesIO(bytes(html_content, 'utf-8'))

    def create_email(self, attachment: io.BytesIO) -> dict:
        """Create the email."""
        body = 'SWAT generated email with HTML attachment.'
        message = MIMEMultipart()
        message['to'] = self.args.recipient
        message['from'] = self.args.sender
        message['subject'] = self.args.subject
        message.attach(MIMEText(body, 'plain'))

        # Decode the bytes to a string before passing to MIMEText
        html_attachment = MIMEText(attachment.getvalue().decode('utf-8'), 'html')
        html_attachment.add_header('Content-Disposition', 'attachment', filename=f'{self.args.attachment}.html')

        message.attach(html_attachment)
        self.elogger.info(f'Created email and attached HTML')
        return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

    def send_email(self, email: dict) -> None:
        """Send the email."""
        self.service.users().messages().send(userId='me', body=email).execute()
        self.elogger.info(f'Sent email to {self.args.recipient} from {self.args.sender}')
        self.elogger.info(f'Email subject: {self.args.subject}')

    def execute(self) -> None:
        self.elogger.info(self.exec_str(self.parser.description))
        html_attachment = self.create_html()
        email = self.create_email(html_attachment)
        self.send_email(email)
