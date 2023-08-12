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
    <a href="https://github.com/elastic/SWAT/issues/">Report Bug</a>
  <span> · </span>
    <a href="https://github.com/elastic/SWAT/issues/">Request Feature</a>
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
