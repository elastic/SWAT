Prerequisites
=============

SWAT is a tool that emulates a Google Workspace environment. It's imperative to have a Google Workspace account with administrative privileges to utilize SWAT. This tool is not intended for use with personal Google accounts.
SWAT was developed to be used in a lab environment, and it's not recommended to use it in a production environment. It's also not recommended to use SWAT with a Google Workspace account that's already in use.

Organization
------------

Google Workspace Account, Domain, and License
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- **Account**: It's imperative to have a valid Google Workspace account.
- **Domain**: The domain associated with your Google Workspace.
- **License**: Ensure you have the appropriate Google Workspace license.

Credentials
-----------

Service Accounts
^^^^^^^^^^^^^^^^

- **Create a Service Account**: Navigate to the `GCP Console <https://console.cloud.google.com/>`_ and under the project, create a service account within the IAM & Admin section.
- **Assign Roles**: This service account should be endowed with roles such as "Project Editor" to manage resources.

For the effective use of service accounts, it's imperative to enable Domain-Wide Delegation in the Google Workspace Admin console. Then, associate the service account you've created. Comprehensive information on this can be accessed `here <https://developers.google.com/cloud-search/docs/guides/delegation>`_.

OAuth 2.0 Client IDs
^^^^^^^^^^^^^^^^^^^^

For SWAT to operate effectively, it needs to be registered as an application for each intended Google Workspace organization. For instance, if you're planning to utilize a Google Workspace account in one organization, and another in a different one, or just a solitary user account for emulation, SWAT requires registration with every organization.

- **Create OAuth 2.0 Client ID**: Within the GCP console, generate an OAuth 2.0 Client ID on the 'Credentials' page.
- **Download Credentials**: Secure a JSON file that contains both Client ID and Client Secret.

If this is your maiden attempt, setting up the OAuth consent screen for your applications in the current project might be necessary. Detailed guidelines are available `here <https://support.google.com/cloud/answer/6158849?hl=en>`_.
For a detailed guide on how to create OAuth creds and use them with SWAT, refer to the `SWAT setup guide <https://swat.readthedocs.io/en/latest/how_to_guides.html>`_.

Enabled APIs and Domain-Wide Delegation
---------------------------------------

Domain-Wide Delegation (DWD)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- **Enable DWD**: Activate DWD for your service account in the GCP console.
- **Delegate Required Scopes**: Precisely define OAuth scopes for services such as Gmail, Drive, and Calendar.

Enable Google Workspace APIs
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- **Activate APIs**: Generally, for SWAT's core functionalities, activating the Gmail API, Drive API, and Google Calendar API is mandatory.

Google Cloud Platform (GCP) Requirements
----------------------------------------

Billing Account
^^^^^^^^^^^^^^^

- **Link a Billing Account**: This is imperative for accessing non-free tier GCP resources.

Local Python Environment
------------------------

- **Python 3.10+**: SWAT is optimized to operate on Python 3.10 or its higher versions.
- **Dependencies**: Utilize `pip` to install the required dependencies delineated in SWAT's requirements file.

Conclusion
----------

Setting up SWAT demands meticulous attention to both details and permissions. Adhering to these prerequisites ensures that SWAT operates flawlessly within your Google Workspace realm. For granular, step-by-step guidance, consult Google's official documentation or the comprehensive SWAT setup guide.

When developing SWAT, we meticulously constructed our own lab environment and Google Domain, ensuring a seamless experience from an admin perspective. This tool is tailored for someone already equipped with an account with administrative privileges, granting access to amenities such as the Google Workspace admin console, GCP console, and similar platforms.

Stay vigilant, and here's to efficient emulation!
