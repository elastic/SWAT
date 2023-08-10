import io
import os
import shutil
import tempfile
import time

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

from swat.emulations.base_emulation import BaseEmulation
from swat.utils import ETC_DIR, get_chromedriver


class Emulation(BaseEmulation):
    parser = BaseEmulation.load_parser(description='Stages sensitive encryption key files in Google Drive and accesses them via shared links.')
    parser.add_argument('folder_id', help='Google Drive Folder ID')
    parser.add_argument('--cleanup', action='store_true', help='Clean up staged files after execution')

    techniques = ['T1530']
    name = 'Download Stored Encryption Keys'

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.folder_id = self.args.folder_id
        self.service = build('drive', 'v3', credentials=self.obj.cred_store.store['default'].session)
        self.file_extensions = ["token", "assig", "pssc", "keystore", "pub", "pgp.asc", "ps1xml", "pem", "gpg.sig"]

    def stage_files(self) -> list[str]:

        shareable_links = []

        for ext in file_extensions:
            file_name = f"fake_file.{ext}"
            file_content = f"This is a fake {file_name}"  # You can customize the content

            # Write the content to a temporary file
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(file_content.encode('utf-8'))
                temp_path = temp_file.name

            # Use the temporary file path for MediaFileUpload
            media = MediaFileUpload(temp_path, mimetype='text/plain', resumable=True)
            file_metadata = self.service.files().create(media_body=media,
                                                        body={'name': file_name, 'parents': [self.folder_id]}).execute()
            os.unlink(temp_path)  # Delete the temporary file

            # Change file permission to allow anyone with the link to view
            self.service.permissions().create(fileId=file_metadata['id'],
                                            body={'role': 'reader', 'type': 'anyone'}).execute()

            # Create a shareable link
            shareable_link = f"https://drive.google.com/file/d/{file_metadata['id']}/view"
            shareable_links.append(shareable_link)

            self.elogger.info(f"Staged {file_name} with shareable link: {shareable_link}")

        return shareable_links


    def access_files(self, share_links) -> None:
        '''Access the staged files via shared links.'''

        self.elogger.info(f'Accessing staged files via shared links')
        driver = get_chromedriver()

        # Open each share link in Chrome
        for link in share_links:
            driver.get(link)
            self.elogger.info(f"Accessed {link}")
            time.sleep(1)  # You can modify the sleep time

        # Close Chrome
        driver.quit()

    def cleanup(self):
        '''Clean up staged files from Google Drive.'''
        # Query the files in the specified folder
        results = self.service.files().list(q=f"'{self.folder_id}' in parents").execute()
        files = results.get('files', [])

        # Delete each file
        for file in files:
            self.service.files().delete(fileId=file['id']).execute()
            self.elogger.info(f"Deleted {file['name']} from Google Drive")

    def execute(self) -> None:
        '''Main execution method.'''
        self.elogger.info(self.exec_str(self.parser.description))
        share_links = self.stage_files()
        self.access_files(share_links)
        if self.cleanup:
            self.cleanup()
