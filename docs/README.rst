====================================
SWAT (Simple Workspace ATT&CK Tool)
====================================

.. image:: https://readthedocs.org/projects/swat/badge/?version=latest
   :target: https://swat.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

.. image:: https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54
   :target: https://www.python.org/downloads/
   :alt: Python

.. image:: https://img.shields.io/badge/ATT&CK-Navigator-red.svg?style=for-the-badge&logoColor=white
   :target: https://attack.mitre.org/matrices/enterprise/cloud/googleworkspace/
   :alt: ATT&CK Coverage

.. image:: https://img.shields.io/badge/Google_Cloud-4285F4?style=for-the-badge&logo=google-cloud&logoColor=white
   :target: https://workspace.google.com/
   :alt: Google Cloud

Description
===========

SWAT (Simple Workspace ATT&CK Tool) is a robust red teaming tool tailored for Google Workspace environments. Its primary aim is to assist Elastic rule authors, threat researchers, and the broader community with simulated attack exercises against Google Workspace infrastructures. The overarching goal is to drive threat research and craft precise detection rules. SWAT emphasizes simplicity, intuitiveness, and is rooted in the MITRE ATT&CK framework. However, its straightforward nature doesn't limit its flexibility. Its modular architecture encourages users and community members to extend its functionalities seamlessly.

Google Workspace, widely known as GSuite previously, is a collection of Google's digital services, such as Gmail, Drive, Docs, and Sheets. Its vast features set makes it a staple for numerous businesses, from startups to large corporations. With such widespread usage, it becomes an enticing target for cyber threat actors with varying objectives, from data breaches to system compromises. SWAT, envisioned by the Threat Research and Detection Engineering (TRaDE) team at Elastic, emerges as a crucial tool for evaluating detection rule effectiveness and hosting red teaming exercises for Google Workspace environments.

Features
========

* MITRE ATT&CK: SWAT is built around the MITRE ATT&CK framework.
* Google Workspace: Specifically tailored for Google Workspace.
* Emulations: Several adversary techniques are available out of the box.
* Commands: Equipped with commands aiding in emulations, ATT&CK coverage, auditing, and more.
* Extensible: Built with extensibility at its core.
* Easy to use: Offers a simple and intuitive command line interface.
* Credential Store: Maintains credentials and authenticated sessions for emulations.
* Logging: All general outputs and emulation results are diligently logged.
* Auditing: Enables Google Workspace log audits for specific events.
* Global Variables: Lets you define global variables applicable for commands and emulations.

Installation
============

1. **Install Python 3**: Grab Python 3 from Python's `official website <https://www.python.org/downloads/>`_.
2. **Create a Virtual Environment**: Execute `python3 -m venv swat-env` in your desired location.
3. **Activate the Virtual Environment**: Use `source swat-env/bin/activate (macOS/Linux)` or `swat-env\Scripts\activate (Windows)`.
4. **Install Poetry**: Adhere to the installation instructions on `Poetry's official website <https://python-poetry.org/docs/#installation>`_.
5. **Clone SWAT Repository**: Fetch the SWAT repository from GitHub.
6. **Install SWAT**: Switch to the SWAT directory and fire `poetry install`.
7. **Link SWAT Command**: Establish a link for the SWAT command as needed.
8. **Start SWAT Shell**: Launch with `swat` or `poetry run swat`.

Documentation
=============

The comprehensive documentation is available on ReadTheDocs: `SWAT Documentation <https://swat.readthedocs.io/>`_. Developers keen on diving deeper into the code or contributing can begin with the `Developer's Guide <https://swat.readthedocs.io/en/latest/developers.html>`_.

Inspirations
============

The birth of SWAT was influenced by several pioneering projects:

- `Elastic Dorothy <https://github.com/elastic/dorothy>`_
- `Endgame's Red Team Automation (RTA) <https://github.com/endgameinc/RTA>`_
- `Red Canary's Atomic Red Team <https://github.com/redcanaryco/atomic-red-team>`_
- `Splunk's Attack Range <https://github.com/splunk/attack_range>`_
- `MITRE's Caldera <https://github.com/mitre/caldera>`_

Drawing from these inspirations and addressing the unique challenges of red teaming within Google Workspace, SWAT stands as an embodiment of collaborative and purposeful development.

Contribution
============

Your contributions can shape SWAT! Dive into our `Contributing Guide <https://swat.readthedocs.io/en/latest/contributing.html>`_ for details.

Support
=======

Encountering issues? Reach out! Initiate a `discussion <https://github.com/elastic/SWAT/discussions>`_ on our GitHub repository.

Disclaimer
==========

- This project is in its early stages of development and should be considered in a pre-alpha or infancy stage. The codebase, features, and overall functionality are under active development, and there will be many updates, changes, and enhancements in the foreseeable future.
- While we believe in transparency and inclusivity, and we're excited to share our project and roadmap with the community, we want to be clear that certain features may be incomplete, or the software may exhibit unexpected behaviors. Therefore, the use of this software in a production environment or for critical applications is not recommended at this stage.
- We warmly welcome contributions, feedback, and community engagement. Feel free to explore the code, experiment with it, and contribute to its development.
- We're committed to creating a simple but efficient tool for emulation in Google Workspace while in parrellel conducting threat research in this ecostystem, and as such, we'll be regularly updating the code and communicating changes through issues and discussions. However, please note that as the project evolves, certain features may be altered, deprecated, or removed.
- Your understanding and participation in this early phase are highly appreciated. For any questions, concerns, or suggestions, please feel free to open an issue or contact us directly.
- Obtain the proper authorization before using SWAT in an environment that you do not own and administer. Users take full responsibility for the outcomes of using SWAT.
- SWAT is not affiliated with or endorsed by Google.
- Thank you for your interest in our project, and we look forward to building something great together!

License
=======

SWAT is open-source, licensed under the Apache License, Version 2.0. Delve into the LICENSE file for comprehensive details or visit `Apache License 2.0 <http://www.apache.org/licenses/>`_.
