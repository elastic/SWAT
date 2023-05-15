import http.server
import smtplib
import socketserver
import threading
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

import yaml
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from swat.commands.base_command import BaseCommand
from swat.commands.emulate import AttackData


class Command(BaseCommand):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        with open(Path(__file__).with_suffix('.yaml')) as config_file:
            self.config = yaml.safe_load(config_file)


    def create_file(self):
        staging_dir = Path.cwd() / 'staging'  # Current working directory / 'staging'
        staging_dir.mkdir(exist_ok=True)  # Create 'staging' directory if it doesn't exist

        # Create 'hello_world.txt' in the 'staging' directory
        file_path = staging_dir / self.config['email']['file_name']
        with file_path.open(mode='w') as file:
            file.write(self.config['email']['file_contents'])

        self.file_path = str(file_path)  # Save the file path for later use

    def start_http_server(self):
        PORT = 8000
        Handler = http.server.SimpleHTTPRequestHandler
        self.httpd = socketserver.TCPServer(("", PORT), Handler)
        self.server_thread = threading.Thread(target=self.httpd.serve_forever)
        self.server_thread.start()
        self.logger.info("HTTP server started...")

    def stop_http_server(self):
        self.httpd.shutdown()
        self.server_thread.join()
        self.logger.info("HTTP server stopped.")

    def send_email(self):
        # Create a relative path for the file
        relative_path = Path("staging", self.config['email']['file_name'])

        msg = MIMEMultipart()
        msg['From'] = self.config['external_account']['email']
        msg['To'] = self.config['target_user']
        msg['Subject'] = self.config['email']['subject']
        body = self.config['email']['body'] + f' http://localhost:8000/{relative_path}'
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(self.config['external_account']['email'], self.config['external_account']['app_password'])
        text = msg.as_string()
        server.sendmail(self.config['external_account']['email'], self.config['target_user'], text)
        server.quit()

    def execute(self, attack: AttackData) -> None:
        self.logger.info(f"Executing emulation for {attack}")

        self.create_file()
        self.start_http_server()
        self.send_email()
        time.sleep(self.config['server']['sleep'])  # Wait for 1 minute
        self.stop_http_server()