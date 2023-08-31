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

import os
import shutil
import tempfile
import time

import requests
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from swat.emulations.base_emulation import BaseEmulation


class Emulation(BaseEmulation):
    """
    Stages text files with sensitive encryption key file extensions in Google Drive and accesses them via shared links.
    """
    parser = BaseEmulation.load_parser(description='Stages sensitive encryption key files in Google Drive and accesses them via shared links.')
    parser.add_argument('session_key', default='default', help='Session to use for service building API service')
    parser.add_argument('folder_id', help='Google Drive Folder ID')
    parser.add_argument('--cleanup', action='store_true', default=False, help='Clean up staged files after execution')

    techniques = ['T1552.004']
    name = 'Access Stored Keys and Tokens in Drive'
    scopes = ['drive.file','drive.readonly','drive']
    services = ['drive']
    description = "Stages sensitive encryption key files in Google Drive and accesses them via shared links."
    references = ["https://github.com/elastic/detection-rules/blob/main/rules/integrations/google_workspace/credential_access_google_workspace_drive_encryption_key_accessed_by_anonymous_user.toml"]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.folder_id = self.args.folder_id
        self.service = build('drive', 'v3', credentials=self.obj.cred_store.store[self.args.session_key].session)
        # file extensions filtered to 5 for testing purposes
        self.file_extensions = [
            "token","assig", "pssc", "keystore", "pub", "pgp.asc", "ps1xml", "pem", "gpg.sig", "der", "key","p7r",
            "p12", "asc", "jks", "p7b", "signature", "gpg", "pgp.sig", "sst", "pgp", "gpgz", "pfx", "crt", "p8", "sig",
            "pkcs7", "jceks", "pkcs8", "psc1", "p7c", "csr", "cer", "spc", "ps2xml"
        ]

    def stage_files(self) -> list[str]:
        """Stage files in Google Drive and return a list of shareable links."""
        shareable_links = []

        for ext in self.file_extensions:
            try:
                file_name = f"fake_file.{ext}"
                file_content = f"This is a fake {file_name}"

                with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                    temp_file.write(file_content.encode('utf-8'))
                    temp_path = temp_file.name

                media = MediaFileUpload(temp_path, mimetype='text/plain', resumable=True)
                file_metadata = self.service.files().create(media_body=media,
                                                            body={'name': file_name, 'parents': [self.folder_id]}).execute()

                os.unlink(temp_path)

                self.service.permissions().create(fileId=file_metadata['id'],
                                                body={'role': 'reader', 'type': 'anyone'}).execute()

                shareable_link = f"https://drive.google.com/file/d/{file_metadata['id']}/view"
                shareable_links.append(shareable_link)

                self.elogger.info(f"Staged {file_name} with shareable link: {shareable_link}")

            except Exception as e:
                self.elogger.error(f"Error while staging file with extension {ext}. Error: {str(e)}")

        return shareable_links

    def access_files(self, share_links) -> None:
        """Access the staged files via shared links and download them."""

        try:
            self.elogger.info(f'Accessing staged files via shared links')
            s = requests.Session()
            s.headers.update({'User-Agent': 'Simple Workspace ATT&CK Tool (SWAT)'})
            s.headers.update({'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'})
            s.headers.update({'Accept-Encoding': 'gzip, deflate, br'})
            s.headers.update({'Accept-Language': 'en-US,en;q=0.5'})
            s.headers.update({'Connection': 'keep-alive'})

            for link in share_links:
                file_id = link.split('/')[-2]
                s.get(link)
                self.elogger.info(f"Accessed file at {link}")
                download_link = f"https://drive.google.com/uc?export=download&confirm=no_antivirus&id={file_id}"
                retrieved_file = s.get(download_link)
                with open(f"{self.artifacts_path}/file_{file_id}", 'wb') as f:
                    f.write(retrieved_file.content)
                self.elogger.info(f"Downloaded file from {download_link}")
                time.sleep(1)

            s.close()

        except Exception as e:
            self.elogger.error(f"Error accessing or downloading files. Error: {str(e)}")

    def cleanup(self) -> None:
        """Clean up staged files from Google Drive."""
        try:
            results = self.service.files().list(q=f"'{self.folder_id}' in parents").execute()
            files = results.get('files', [])

            for file in files:
                self.service.files().delete(fileId=file['id']).execute()
                self.elogger.info(f"Deleted {file['name']} from Google Drive")

            shutil.rmtree(self.artifacts_path)
            self.logger.info(f"Deleted local artifacts directory: {self.artifacts_path}")

        except Exception as e:
            self.elogger.error(f"Error during cleanup. Error: {str(e)}")

    def execute(self) -> None:
        """Main execution method."""
        self.elogger.info(self.exec_str(self.parser.description))
        try:
            share_links = self.stage_files()
            self.access_files(share_links)
            if self.args.cleanup:
                self.cleanup()

        except Exception as e:
            self.elogger.error(f"Error during execution. Error: {str(e)}")
