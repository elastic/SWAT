Getting Started
===============

Authentication with GCP
-----------------------

For SWAT to effectively carry out emulations and auditing, it requires a valid authentication session. This authentication is facilitated through Google Cloud Platform (GCP) using OAuth. Here's how you can set it up:

1. **Acquire OAuth Credentials from GCP**:
   Ensure you have the OAuth credentials for your application from GCP. These credentials typically come in the form of a JSON file. We recommend following the steps provided by Google to `create OAuth client creds <https://developers.google.com/workspace/guides/create-credentials#oauth-client-id>`_.

2. **Save the Credentials Locally**:
   Store the credentials file in a known path on your local system. Be sure to keep this file safe, as it contains sensitive information.

3. **Initialize Authentication Session in SWAT**:
   Launch the SWAT shell and run the following command:

   .. code-block:: bash

      auth session --store-key default --creds PATH_TO_FILE

   Replace `PATH_TO_FILE` with the path to your saved OAuth credentials file.

4. **Complete the OAuth Authorization Workflow**:
   After running the above command, you will be guided through the OAuth authorization workflow. This will involve logging into the relevant Google account and providing the necessary consents for the SWAT application.

5. **Validation**:
   Once the workflow is complete, SWAT will store a valid session in its Credential Store. This session is crucial for running most emulations and the audit command within SWAT. Always ensure you have an active session before proceeding with these operations.

Note: Maintaining a valid authentication session ensures SWAT can interact seamlessly with Google Workspace, allowing for accurate emulations and effective auditing. A detailed guide on authentication/authorization with SWAT can be found `here <https://swat.readthedocs.io/en/latest/auth.html>`_.

Starting Steps
--------------

To get the most out of SWAT, follow these steps to ensure a smooth setup and exploration experience:

1. **Initialize the SWAT Shell**:
   After installation, start the SWAT shell. This shell will be your primary interface for running commands and emulations.

   .. image:: _static/swat_started.png
      :width: 600px
      :alt: Starting SWAT Shell

2. **Explore Available Commands**:
   Within the SWAT shell, enter the `help` command. This will provide an overview of all available commands. To understand the specifics of a command, type `help <command_name>`.

   .. image:: _static/help_command.png
      :width: 600px
      :alt: `help` command execution to see available commands

3. **Ensure Authentication**:
   Before diving into emulations, make sure you've followed the steps in the "Authentication with GCP" section above. To check you can run ``auth list`` or ``creds list`` to see your stored sessions or credentials.

4. **Discover Out-of-the-Box Emulations**:
   SWAT provides several built-in emulations. To view and understand these, run the command `help emulate`. This command will show you existing emulations, their required scopes and APIs required.

   .. image:: _static/help_emulation_command.png
      :width: 600px
      :alt: `help emulate` command to see available emulations

5. **View MITRE ATT&CK Coverage**:
   Interested in understanding the coverage provided by SWAT against the MITRE ATT&CK framework? Run the `coverage view` command. This will present all techniques and tactics covered by SWAT.

   .. image:: _static/coverage_view_command.png
      :width: 600px
      :alt:   `coverage view` command to see MITRE ATT&CK coverage

6. **Deep Dive into Command Details**:
   As you become familiar with the available commands, remember that each one has a detailed help definition. So, if you're ever in doubt or need more information about a command, just type `help <command_name>`.

   .. image:: _static/help_auth_session_command.png
      :width: 600px
      :alt: `help auth session` command

7. **Stay Updated**:
   Periodically check for updates or new additions to the tool. SWAT is continually evolving, and staying updated ensures you have the latest capabilities at your fingertips.

Remember, SWAT is designed to be intuitive and user-friendly. As you spend more time with the tool, its operations will become second nature. Happy emulating!