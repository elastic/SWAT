# SWAT - Simple Workspace ATT&CK Tool
[![Supported Python Versions](https://img.shields.io/badge/python-3.10+-red.svg?style=for-the-badge&logo=python)](https://www.python.org/downloads/)
[![Supported Go Versions](https://img.shields.io/badge/golang-20.03+-red.svg?style=for-the-badge&logo=go)](https://go.dev/dl/)
[![ATT&CK Coverage](https://img.shields.io/badge/ATT&CK-Navigator-red.svg?style=for-the-badge)](https://ela.st/detection-rules-navigator)

SWAT is a simple red teaming tool designed specifically for red teaming exercises against Google Workspace environments. The tool maps closely to the MITRE ATT&CK framework, providing an interactive command-line interface and shell to simulate cyber attacks and evaluate the effectiveness of an organization's security controls. Built with Python, YAML, and GoLang, this tool helps penetration testers, security professionals, and ethical hackers simulate the malicious behavior of adversaries against Google Workspace environments.

## Table of Contents

- [SWAT - Simple Workspace ATT\&CK Tool](#swat---simple-workspace-attck-tool)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
    - [Setup Google Workspace Environment](#setup-google-workspace-environment)
    - [Setup Credentials](#setup-credentials)
    - [Initiate Shell](#initiate-shell)

## Features

- Interactive command-line interface and shell
- Commands to carry out red teaming techniques
- Maps closely to the MITRE ATT&CK framework
- Includes a cross-platform C2 payload
- Gmail phishing kit
- Generated Jupyter Notebooks for data analysis
- Supports Python, YAML, and Golang

## Prerequisites
SWAT requires simple Google Workspace and GCP environments to be setup prior to use. This includes a domain registered to Google Workspace with at least a [Business Starter](https://workspace.google.com/pricing.html) license. This gives access to the [Google Workspace admin console](https://admin.google.com) by the administrator account. This administrator account can then be used to login to the [GCP console](https://console.cloud.google.com/) where Google Workspace APIs are managed.


## Installation

1. Clone the repository: `git clone git@github.com:elastic/SWAT.git`
2. Change to the repository directory: `cd SWAT`
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

```console
swat --credentials path/to/credentials.json --token path/to/token.pickle
```
















