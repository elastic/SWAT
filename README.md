#

<div align="center">
  <h1>SWAT - Simple Workspace ATT&CK Tool</h1>

  <p>
    SWAT is a simple attack tool designed specifically for red teaming exercises against Google Workspace environments to aid detection engineers with rule development.
  </p>

<!-- Badges -->

[![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://www.python.org/downloads/)
[![ATT&CK Coverage](https://img.shields.io/badge/ATT&CK-Navigator-red.svg?style=for-the-badge&logoColor=white)](https://attack.mitre.org/matrices/enterprise/cloud/googleworkspace/)
[![Google Cloud](https://img.shields.io/badge/Google_Cloud-4285F4?style=for-the-badge&logo=google-cloud&logoColor=white)](https://workspace.google.com/)


<h5>
    <a href="https://github.com/elastic/SWAT/issues/new?assignees=&labels=bug&projects=&template=bug_report.md&title=%5BBug%5D+Brief+description+of+the+bug">Report Bug</a>
  <span> · </span>
    <a href="https://github.com/elastic/SWAT/issues/new?assignees=&labels=enhancement%2C+python%2C+module%2C+Google+Workspace&projects=&template=module_feature_request.md&title=%5BFeature+Request%5D+Add+emulation+module+for+%5BTechnique%5D">Emulation Request</a>
  <span> · </span>
    <a href="https://github.com/elastic/SWAT/issues/new?assignees=&labels=enhancement%2C+python%2C+module%2C+Google+Workspace&projects=&template=command_feature_request.md&title=%5BFeature+Request%5D+Add+command+module+for+%5BCommand%5D">Command Request</a>
  <span> · </span>
    <a href="https://github.com/elastic/SWAT/issues/new?assignees=&labels=enhancement%2C+core-code%2C+feature-request&projects=&template=feature_request.md&title=%5BFeature+Request%5D+Feature%2FUpdate+Request+for+SWAT">Feature Request</a>
  <span> · </span>
    <a href="https://github.com/elastic/SWAT/issues/new?assignees=&labels=other&projects=&template=other.md&title=%5BOther%5D+Brief+description+of+the+issue">Other</a>
  </h5>
</div>

<br />

SWAT maps closely to the MITRE ATT&CK framework, providing an interactive command-line interface and shell to simulate cyber attacks and evaluate the effectiveness of an organization's security controls. Built with Python and YAML, this tool helps detection engineers and red-teamers emulate suspicious adversary behavior against Google Workspace environments.

https://github.com/elastic/SWAT/assets/99630311/6436071f-2bdd-4d09-917e-b2b6795743c7

## Features

- Interactive command-line interface and shell
- Modular design for simple command or emulation additions
- Credential store for credentials and active sessions
- Maps closely to the MITRE ATT&CK framework
- Audit command for Google Workspace service log retrieval
- Coverage command to view correlation between emulations and MITRE ATT&CK
- Helper methods and functions for different emulation scenarios
- Supports Python and YAML

## Getting Started
To get started, navigate to the SWAT [wiki](https://github.com/elastic/SWAT/wiki).

## Disclaimer
Obtain the proper authorization before using SWAT in an environment that you do not own and administer. Users take full responsibility for the outcomes of using SWAT. SWAT is licensed under [Apache License Version 2.0](LICENSE.txt).
