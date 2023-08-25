Developer's Guide for SWAT
==========================

SWAT (Simple Workspace ATT&CK Tool) is designed with a modular architecture, emphasizing extensibility and ease of integration for new functionalities. This document delves into its architectural pillars, aiming to offer developers a comprehensive understanding of its design principles and workflows.

Development Environment Setup
-----------------------------

From a threat detection engineer perspective, a development Google Workspace environment is recommended. This requires the following basic steps to get started:

1. A Google Workspace account and domain registered through Google.
2. A Google Workspace business license for the administrative account. This will allow you to create a Google Workspace organization. This will also allow you to create a Google Cloud Platform (GCP) project and have access to the Google Cloud Console.
3. OAuth 2.0 credentials for the GCP project, accessible from the Google Cloud Console. The OAuth 2.0 consent screen should be configured for internal use only. Credentials should be downloaded and accessible to SWAT.

At this point you have a basic lab environment for development. If you are an active administrator of a Google Workspace environment, you can use your production environment for development. However, it is recommended to use a development environment to avoid any potential issues. A separate GCP project is also recommended to avoid any potential issues.
If you choose to use a production environment, we recommend you use emulations with a cleanup method to undo any changes made by SWAT.

An example of setting up a development environment can be found in `Google Workspace Attack Surface Part Two: Setup Threat Detection With Elastic <https://www.elastic.co/security-labs/google-workspace-attack-surface-part-two>`_.

SWAT requires a Python 3.10+ virtual environment and requires the following basic steps to get started:

1. Install Python 3.10+.
2. Create a virtual environment.
3. Clone or fork the SWAT repository.
4. Install the SWAT package with poetry.
5. Setup debugging in your IDE of choice.
6. Ensure source control is setup correctly for GitHub.

A more detailed can be found in SWAT's `Getting Started Documentation <https://swat.readthedocs.io/en/latest/getting_started.html>`_.

Debugging
---------
SWAT was developed using both VSCode and PyCharm. Of course, you can use any IDE you want, but the following debug configuration is for VSCode.

.. code-block:: json
   :caption: VSCode debug configuration for SWAT
   :name: VSCode debug configuration for SWAT

    {
        "version": "0.2.0",
        "configurations": [
        {
            "name": "Python: SWATShell",
            "type": "python",
            "request": "launch",
            "module": "swat.main",
            "justMyCode": false
        }
        ]
    }

1. Add a new debug configuration for your IDE of choice.
    #. The example above is for VSCode.
    #. It is important to point to the `swat.main` module as this is the entry point for SWAT and starts the shell.
2. Start the debugger which will start the SWAT shell.
3. You can now set breakpoints in your IDE.
4. Execute a command or emulation and the debugger will stop at the breakpoint.
5. When executed, regardless of error or success, the debugger return you back to the shell.


SWAT's Modular Architecture
---------------------------

SWAT was designed to be simple and modular. It is built on a modular design principle, with each emulation and command encapsulated as a distinct module, ensuring ease of management, testing, and extension. The following sections will discuss the core components of SWAT and how they work together.

1. **Main Entry Point (`main.py`):**
   The main entry point of SWAT where the execution begins. It initializes the shell and takes care of high-level functions.

2. **Interactive Shell (`shell.py`):**
   Provides an interactive command-line interface to interact with the various SWAT functionalities. Commands are parsed and executed here.

3. **Base (`base.py`):**
   The foundation for the rest of the modules. Contains essential utilities and base functionalities used throughout the framework.

4. **Base Emulation (`base_emulation.py`):**
   The foundational class for all emulation modules. It provides a structure and common methods for emulations to ensure consistency and reusability.

5. **Base Command (`base_command.py`):**
   A base class that offers core structures and functionalities for individual command modules.

6. **Emulations (`emulations/`):**
   Contains all the emulations that SWAT can execute. Each emulation is a distinct module that inherits from `BaseEmulation`. These modules are in categorized folders according to MITRE ATT&CK tactics.

7. **Commands (`commands/`):**
   Contains all the commands that SWAT can execute. Each command is a distinct module that inherits from `BaseCommand`.

8. **Logging (`logger.py`):**
   Provides logging facilities for the framework for console and file output. It is used by all modules to ensure consistent logging across the framework. A global file and console handler are configured by default. When emulations occur in parallel, a separate file handler is created for each emulation.

9. **Argparse:**
   The Python standard library for parsing command-line arguments. It is used by all commands and emulations to parse and validate arguments. It tailors well to the modular design of SWAT, allowing each module to define its own arguments.

10. **Credential Store (`credential_store.py`):**
    A simple credential store built on custom data classes for Google Workspace OAuth, Service Account and API credentials. It is used to store and retrieve credentials and sessions for emulations and commands. This allows for a single source of truth for credentials and sessions across the framework when running commands and emulations. For persistence, credentials are saved on shell exit to a pickle file and loaded on shell start.

SWAT Design Principles
----------------------

1. **Modularity:**
   SWAT is built on a modular design principle. Each emulation and command is encapsulated as a distinct module, ensuring ease of management, testing, and extension.

2. **Dynamic Importing:**
   SWAT employs dynamic importing to load emulations and commands at runtime. This approach promotes the seamless integration of new modules without necessitating alterations to the core framework.

3. **Base SWAT Object (`base.py`):**
   Central to SWAT's design is the base object. This object encapsulates shared attributes and methods, ensuring consistent access to configurations, the credential store, and logging facilities across emulations and commands.

4. **Emulation & Command Workflow:**
   The workflows for emulations and commands are kept distinct yet are built upon shared foundational classes (`BaseEmulation` and `BaseCommand`). This ensures consistent behavior across different operations while accommodating their unique requirements.

5. **Logging:**
   Logging is a core component of SWAT, ensuring consistent logging across the framework. It is used by all modules to ensure consistent logging across the framework. A global file and console handler are configured by default. When emulations occur in parallel, a separate file handler is created for each emulation.

6. **Data Classes:**
   Data classes are used throughout SWAT to ensure consistency and ease of use. They are used for the credential store and other functionalities.

Modules & Components
--------------------

**Emulation Modules:**

Emulation modules are the core of SWAT. They encapsulate the logic for emulating adversary behaviors and are the primary means of interacting with external services. Emulations are categorized according to MITRE ATT&CK tactics, with each tactic having its own folder. Emulations are loaded dynamically at runtime, ensuring extensibility and ease of integration.

The `emulate` command is used to execute emulations by dynamically loading the required module and executing its `execute()` method.

Additional Notes:
   - Located in `swat/emulations/`.
   - Each emulation follows a specific structure, inheriting from `BaseEmulation` in `base_emulation.py`.
   - It contains parser configurations, initialization methods, and core emulation functionalities.
   - Example: The `gmail_html_with_embedded.js.py` module that sends phishing emails with HTML attachments.

For more information, see the `Emulations Documentation <https://swat.readthedocs.io/en/latest/emulations.html>`_.

**Command Modules:**

Command modules are at the core of SWAT's functionality. They encapsulate the logic for executing specific tasks, such as authentication, data retrieval, and other operations. Commands are loaded dynamically at runtime, ensuring extensibility and ease of integration.

- Located in `swat/commands/`.
- Each command inherits from `BaseCommand` in `base_command.py`.
- It has parser configurations, initialization methods, and the functionalities for the specific command.
- Example: The `audit.py` module that handles authentication with Google Workspace.

For more information, see the `Adding a Command <https://swat.readthedocs.io/en/latest/commands.html>`_ documentation.

Emulation Workflow
------------------

SWAT uses a six-step workflow for emulations:

1. Run the `emulate` command, which loads the `emulate.py` module and instantiates the `Command(BaseCommand)` class.
2. During instantiation, arguments passed are parsed and validated.
3. Anything within the `SWAT` object from `base.py` is available to the `emulate.py` module through inheritance from `BaseCommand`.
4. The `execute()` method is called in `emulate.py` which locates and loads the emulation module, instantiates the `Emulation(BaseEmulation)` class and calls its `execute()` method.
5. During instantiation, the emulation module inherits from `BaseEmulation` and has access to the `SWAT` object from `BaseCommand` and functionality and attributes from `BaseEmulation`.
6. Arguments passed to the emulation are parsed and validated.
7. The `execute()` method in the emulation module executes the emulation by calling the required methods.
8. Once finished, the `execute()` method returns to the `emulate.py` module which returns the user to the shell.

While not explained in the workflow, each emulation, during instantion will build a service session with the particular Google Workspace API required, passing valid sessions from the Credential Store.

Command Workflow
----------------

SWAT uses a three-step workflow for commands:

1. Run the command, which finds and loads the command module and instantiates the `Command(BaseCommand)` class.
2. During instantiation, arguments passed are parsed and validated.
3. Anything within the `SWAT` object from `base.py` is available to the command module through inheritance from `BaseCommand`.
4. The `execute()` method in the command module executes the command by calling the required methods.
5. Once finished, the `execute()` method returns to the shell.

Extending SWAT
--------------

**Adding New Emulations:**

1. Create a new module in `swat/emulations/`.
2. Add imported for desired functionalities
3. Add `Command` class which takes the `BaseEmulation` class.
4. Add parser configurations for emulation-specific arguments.
5. Add initialization method.
6. Define global self variables.
7. Define the `execute()` method.
8. Add additional methods as needed.

For more information, see the `Adding an Emulation <https://swat.readthedocs.io/en/latest/emulations.html>`_ documentation.

**Adding New Commands:**

1. Create a module in `swat/commands/`.
2. Add imported for desired functionalities
3. Add `Command` class which takes the `BaseCommand` class.
4. Add parser configurations for command-specific arguments.
5. Add initialization method.
6. Define global self variables.
7. Define the `execute()` method.
8. Add additional methods as needed.

For more information, see the `Adding a Command <https://swat.readthedocs.io/en/latest/commands.html>`_ documentation.

Contribution Guidelines
-----------------------

1. **Consistency:** Adhere to the established architecture, ensuring modularity and convention alignment.
2. **Documentation:** Document new methods, classes, and functionalities to maintain clarity.
3. **Testing:** Thoroughly test new functionalities to uphold the SWAT framework's quality.
4. **Authorization:** Ensure that all emulations and commands are authorized for the specific Google Workspace organization being targeted.
5. **Google Policies:** Ensure that all emulations and commands adhere to Google Workspace policies.

Feedback & Questions
--------------------

If you have any feedback or questions about the architecture or the SWAT framework in general, please reach out to the core development team or raise an issue on the GitHub repository.

Contribution Process
--------------------
Please review the existing `contributions guide <swat.readthedocs.io/en/latest/contributing.html>`_ for more information on how to contribute to SWAT.

Tips and Tricks
---------------
Given your experience with SWAT, share any helpful development tips, shortcuts, or best practices that aren't covered in other documents.

