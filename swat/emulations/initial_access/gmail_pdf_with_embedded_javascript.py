import base64
import io
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from googleapiclient.discovery import build
from reportlab.pdfgen import canvas

from swat.emulations.base_emulation import BaseEmulation


class Emulation(BaseEmulation):

    parser = BaseEmulation.load_parser(description='Sends a phishing email to a user with a PDF attachment.')
    parser.add_argument('session_key', default='default', help='Session to use for service building API service')
    parser.add_argument('--recipient', required=True, help='Recipient email address')
    parser.add_argument('--sender', required=True, help='Sender email address')
    parser.add_argument('--subject', default='Phishing Test Email', help='Email subject')
    parser.add_argument('--attachment', default='swat_malicious.pdf', help='Attachment name')

    techniques = ['T1566.001', 'T1204.002']
    name = 'Send PDF with Embedded Javascript with Gmail'
    scopes = ['gmail.send','gmail.readonly','gmail.compose']
    services = ['gmail']

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.service = build('gmail', 'v1', credentials=self.obj.cred_store.store[self.args.session_key].session)

    def create_pdf(self) -> io.BytesIO:
        '''Create a PDF with embedded javascript.'''
        packet = io.BytesIO()
        c = canvas.Canvas(packet)
        c.drawString(100, 100, "SWAT generated PDF")
        c.save()
        packet.seek(0)
        return packet

    def create_email(self, attachment: io.BytesIO) -> dict:
        '''Create the email.'''
        body = 'Click this link generated by SWAT: http://example.com'
        message = MIMEMultipart()
        message['to'] = self.args.recipient
        message['from'] = self.args.sender
        message['subject'] = self.args.subject
        message.attach(MIMEText(body, 'plain'))
        attachment = MIMEApplication(attachment.read(), name=f'{self.args.attachment}.pdf')
        attachment.add_header('Content-Disposition', 'attachment', filename=f'{self.args.attachment}.pdf')
        message.attach(attachment)
        return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

    def send_email(self, email: dict) -> None:
        '''Send the email.'''
        self.service.users().messages().send(userId='me', body=email).execute()

    def execute(self) -> None:
        self.elogger.info(self.exec_str(self.parser.description))
        pdf_attachment = self.create_pdf()
        email = self.create_email(pdf_attachment)
        self.send_email(email)
