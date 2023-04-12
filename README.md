# SWAT
Simple Workspace Offensive Tool (SWAT) is a Python tool for simulating malicious behavior against Google Workspace in reference to the MITRE ATT&CK framework.

# Setup Tool
To get started, do the following steps:

1. Clone the repository locally.
2. From here, setup a virtual python environment with `python 3.8+`.
3. Install requirements by running `pip install -e .`

# Setup Google Workspace Environment
This tool requires a Google Workspace environment with access to GCP for credentials. If not done already, we recommend creating a Google Workspace environment first. After this, please continue to `Setup Credentials` to create credentials.

# Setup Credentials
1. Go to the Google Cloud Console.
2. If you haven't already, create a new project or select an existing one.
3. In the left-side menu, click on "APIs & Services" and then on "Dashboard".
4. Click on "+ ENABLE APIS AND SERVICES" at the top of the page, search for the required Google Workspace APIs (e.g., Google Calendar API, Google Drive API, etc.), and enable them for your project.
5. Go back to the "Dashboard" and click on "Create credentials" at the top of the page.
6. In the "Create credentials" dropdown, select "OAuth client ID".
7. If you haven't already, configure the "OAuth consent screen" with the required information.
8. After configuring the consent screen, choose "Desktop app" as the application type, provide a name for your OAuth client ID, and click "Create".
9. Click "OK" to close the dialog, then click the download icon next to the client ID you just created to download the credentials.json file.


# Initiate Shell
Run the following to start the SWAT shell.

```
swat --credentials path/to/credentials.json --token path/to/token.pickle
```
<img src="/swat/assets/swat_shell.png"  width="500" height="300">