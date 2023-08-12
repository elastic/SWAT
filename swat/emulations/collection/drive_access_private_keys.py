import io
import os
import tempfile
import time
import shutil

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from swat.emulations.base_emulation import BaseEmulation
from swat.utils import get_chromedriver


class Emulation(BaseEmulation):
    parser = BaseEmulation.load_parser(
        description='Stages sensitive encryption key files in Google Drive and accesses them via shared links.')
    parser.add_argument('session_key', default='default', help='Session to use for service building API service')
    parser.add_argument('folder_id', help='Google Drive Folder ID')
    parser.add_argument('--cleanup', action='store_true', default=False, help='Clean up staged files after execution')

    techniques = ['T1552.004']
    name = 'Access Stored Keys and Tokens in Drive'
    scopes = ['drive.file','drive.readonly','drive']
    services = ['drive']

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.folder_id = self.args.folder_id
        creds = self.obj.cred_store.get('default', validate_type='oauth')
        self.service = build('drive', 'v3', credentials=creds.session())
        # file extensions filtered to 5 for testing purposes
        self.file_extensions = [
            "token","assig", "pssc", "keystore", "pub", "pgp.asc", "ps1xml", "pem", "gpg.sig", "der", "key","p7r",
            "p12", "asc", "jks", "p7b", "signature", "gpg", "pgp.sig", "sst", "pgp", "gpgz", "pfx", "crt", "p8", "sig",
            "pkcs7", "jceks", "pkcs8", "psc1", "p7c", "csr", "cer", "spc", "ps2xml"
        ][:5]  # TODO: why create a list and immediate slice it to 5?

    def stage_files(self) -> list[str]:
        """Stage files in Google Drive and return a list of shareable links."""

        shareable_links = []

        for ext in self.file_extensions:
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
        """Access the staged files via shared links and download them."""

        self.elogger.info(f'Accessing staged files via shared links')
        driver = get_chromedriver()

        # Open each share link in Chrome and download the file
        for link in share_links:
            file_id = link.split('/')[-2]  # Extracting the file ID from the share link
            # view the file
            driver.get(link)
            self.elogger.info(f"Accessed file at {link}")
            # download the file
            download_link = f"https://drive.google.com/uc?export=download&confirm=no_antivirus&id={file_id}"
            driver.get(download_link)
            self.elogger.info(f"Downloaded file from {download_link}")
            time.sleep(1)  # You can modify the sleep time, or use WebDriverWait if needed

        # Close Chrome
        driver.quit()

    def cleanup(self) -> None:
        """Clean up staged files from Google Drive."""
        # Query the files in the specified folder
        results = self.service.files().list(q=f"'{self.folder_id}' in parents").execute()
        files = results.get('files', [])

        # Delete each file
        for file in files:
            self.service.files().delete(fileId=file['id']).execute()
            self.elogger.info(f"Deleted {file['name']} from Google Drive")

        # Delete local artifacts directory
        shutil.rmtree(self.artifacts_path)
        self.logger.info(f"Deleted local artifacts directory: {self.artifacts}")

    def execute(self) -> None:
        """Main execution method."""
        self.elogger.info(self.exec_str(self.parser.description))
        share_links = self.stage_files()
        self.access_files(share_links)
        if self.args.cleanup:
            self.cleanup()
