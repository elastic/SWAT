# SWAT - Simple Workspace ATT&CK Tool
[![GitHub License](https://img.shields.io/github/license/{USERNAME}/{REPO_NAME})](LICENSE)
[![GitHub Issues](https://img.shields.io/github/issues/{USERNAME}/{REPO_NAME})](https://github.com/{USERNAME}/{REPO_NAME}/issues)
[![GitHub Stars](https://img.shields.io/github/stars/{USERNAME}/{REPO_NAME})](https://github.com/{USERNAME}/{REPO_NAME}/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/{USERNAME}/{REPO_NAME})](https://github.com/{USERNAME}/{REPO_NAME}/network)

SWAT is a simple red teaming tool designed specifically for red teaming exercises against Google Workspace environments. The tool maps closely to the MITRE ATT&CK framework, providing an interactive command-line interface and shell to simulate cyber attacks and evaluate the effectiveness of an organization's security controls. Built with Python, YAML, and GoLang, this tool helps penetration testers, security professionals, and ethical hackers simulate the malicious behavior of adversaries against Google Workspace environments.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)
- [Disclaimer](#disclaimer)

## Features

- Interactive command-line interface and shell
- Maps closely to the MITRE ATT&CK framework
- Customizable attack scenarios and payloads
- Comprehensive reporting and analytics
- Supports Python, YAML, and GoLang

## Prerequisites

- Google Workspace administrator account with API access
- Python 3.6+
- GoLang 1.14+

## Installation

1. Clone the repository: `git clone https://github.com/{USERNAME}/{REPO_NAME}.git`
2. Change to the repository directory: `cd {REPO_NAME}`
3. Install the required dependencies: `pip install -e .`

### Setup Google Workspace Environment
This tool requires a Google Workspace environment with access to GCP for credentials. If not done already, we recommend creating a Google Workspace environment first. After this, please continue to `Setup Credentials` to create credentials.

### Setup Credentials
1. Go to the Google Cloud Console.
2. If you haven't already, create a new project or select an existing one.
3. In the left-side menu, click on "APIs & Services" and then on "Dashboard".
4. Click on "+ ENABLE APIS AND SERVICES" at the top of the page, search for the required Google Workspace APIs (e.g., Google Calendar API, Google Drive API, etc.), and enable them for your project.
5. Go back to the "Dashboard" and click on "Create credentials" at the top of the page.
6. In the "Create credentials" dropdown, select "OAuth client ID".
7. If you haven't already, configure the "OAuth consent screen" with the required information.
8. After configuring the consent screen, choose "Desktop app" as the application type, provide a name for your OAuth client ID, and click "Create".
9. Click "OK" to close the dialog, then click the download icon next to the client ID you just created to download the credentials.json file.

### Initiate Shell
Run the following to start the SWAT shell.

```
swat --credentials path/to/credentials.json --token path/to/token.pickle
```
<img src="/swat/assets/swat_shell.png"  width="500" height="300">

### Tango Payload
SWAT's Tango payload was developed in GoLang, making it compatible across platforms. Tango is a malicious command-and-control (C2) payload that can be built and distributed to any Windows, Linux or macOS endpoint of choosing. A GCP service account, credentials and specific Google Workspace APIs must be enabled for the payload to operate successfully.

#### Setup Credentials and Enable APIs
1. Setup a service account for Tango in GCP
2. Create credentials for the Tango service account
3. Enable the following Google Workspace APIs for the Tango service account:
   1. Drive API
   2. Sheets API
   3. Docs API
   4. GMail API
   5. Apps Script API

#### Build the Executable from Go

```
cd swat/tango
go build
```

#### Execute Tango Executable
The executable can be executed on the endpoint after distribution. Credentials can be passed into the execution command or can be hardcoded into the binary itself.

Windows
```
TBD
```

Linux
```
TBD
```

macOS
```
TBD
```













