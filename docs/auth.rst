Authentication & Authorization with Google Workspace
====================================================

SWAT integrates seamlessly with Google Workspace, automating security processes. This document offers a granular look at SWAT's authentication and authorization design.

Google Workspace Authentication Mechanisms
------------------------------------------

- **OAuth**: This protocol delegates access using tokens for authentication and authorization. OAuth requires user interaction to grant access to a particular application, in this instance, SWAT.

- **Service Accounts**: Representing non-human users, these accounts authenticate via dedicated credentials. Service accounts are ideal for server-to-server interactions or acting on behalf of a user. Service accounts require domain-wide delegation to access Google Workspace APIs. Unlike OAuth, service account scopes are defined at the time of creation or based on the IAM role assigned. Therefore to use service accounts in SWAT, the user must create a service account with the appropriate scopes and download the JSON key file.

- **API Keys**: These keys authenticate requests to Google Workspace APIs.

For SWAT, both OAuth credentials and Service Account credentials are supported.

The Credential Store (from `base.py`)
-------------------------------------

At its core, the `CredStore` class in `base.py` provides a structured way to handle and store credentials. This is commonly referred to as the "credential store" in SWAT.

1. **Path**: It defaults to `DEFAULT_CRED_STORE_FILE`, pointing to a file where credentials are serialized.
2. **Store**: A dictionary where each key corresponds to a particular `Cred` object. A `Cred` object pairs a credential with an active session, if one exists.

**Key Functionalities**:

- **has_sessions**: A quick boolean check if any stored credentials have an active session.
- **from_file**: Load an instance of `CredStore` from a serialized file.
- **save**: Serialize the current `CredStore` instance to a file.
- **add**: Insert a new `Cred` object into the store.
- **remove**: Remove a `Cred` object using its key.
- **get**: Retrieve a `Cred` object using its key and optionally validate its type.
- **list_credentials**: List all stored credentials.
- **list_sessions**: List all active sessions.

Dataclasses for Credentials
---------------------------

Two primary dataclasses define credentials:

1. **ServiceAccountCreds**: Represents credentials for Google Cloud Platform (GCP) service accounts.
2. **OAuthCreds**: Represents OAuth2.0 application credentials from GCP.

Both classes derive from the `BaseCreds` class and possess:

- **to_dict**: Convert the class instance to a dictionary.
- **from_file**: A class method to instantiate the credential class from a file.

The `Cred` class pairs these credentials with an active session if one exists. The `refreshed_session` method can refresh an expired session.

Command Execution with `auth.py`
--------------------------------

`auth.py` provides the executable logic, allowing the user to:

- Initiate authentication using either OAuth or Service Account.
- Fetch, store, or remove credentials in the `CredStore`.
- Authenticates and authorizes to Google Workspace services with a `Cred` object.

Google Workspace Scopes
-----------------------

Google Workspace services, such as Gmail, Drive, or Calendar, require certain permissions or "scopes" to function. These scopes define what an application can and cannot do. In SWAT, each emulation specifies its required service and scopes.

For example, sending an email via Gmail might require the `gmail.send` scope, while reading might necessitate the `gmail.readonly` scope.

By default, all required scopes for out-of-the-box emulations are defined in `etc/config.yaml` and passed into the authN and authZ flows at time of execution.

To add additional scopes, the user can add them to the `etc/config.yaml` file or or use the `scopes add` command which will add the scopes to the existing scopes from the loaded config file.

Emulation Access to Credential Store
------------------------------------

Emulations have direct access to the `CredStore`. This is because the `SWAT` object from `base.py` is stored during initialization of both `BaseCommand` and `BaseEmulation` classes which are inherited by all commands and emulations, respectively.

- It is recommended to add credentials and authorize prior to emulations so that valid session(s) are available.
- Emulations can access the `CredStore` via `self.obj.cred_store.store[KEY]` where `.session` points to the authN and authZ session.
- To build a service client, typically `self.service = build('SERVICE', 'vN', credentials=self.obj.cred_store.store[KEY].session)` is added to the initialization of the emulation class `Emulation(BaseEmulation)`. Multiple services can be added to the same emulation as long as multiple credentials and sessions are available in the `CredStore`.
- Some OOTB emulations, will include a positional argument `session_key` which is used to select the session from the `CredStore` to use for the emulation.
- These sessions offer authenticated access to specific Google Workspace services, defined in the emulation itself.

For more information on how to authenticate or authorize with credentials in SWAT, please refer to our `Getting Started Guide <https://swat.readthedocs.io/en/latest/getting_started.html>`_ or `How-To Guide <https://swat.readthedocs.io/en/latest/how_to_guides.html>`_.

Persistence of Credentials
--------------------------

Credentials are stored in a serialized file, `swat/etc/.cred_store.pkl`, by default. Both credentials and valid sessions are stored in this file and are loaded at runtime. This allows for persistent authentication and authorization without the need to re-authenticate each time for every user or service account. This can be disabled by changed the `store_on_exit` value in the `etc/config.yaml` to `False`.

Recommendations
---------------

- It is recommended to use at least one OAuth credential with super administrative privileges in SWAT to ensure access to all Google Workspace services and emulations that are OOTB. This ensures not only OOTB emulations can be run but also commands such as `audit`.
- For the default super admin OAuth credentials, it is recommended to authenticate, authorize and store the credentials and session in the credential store with the key name `default` as such ``auth session --store-key default --creds PATH_TO_CREDS``.
- Some emulations require a "3rd-party" google workspace account, separate from the organization being targeted/tested. It is therefore recommended to setup a separate and external Google Workspace account for this purpose.
- For the "3rd-party" Google Workspace account, it is recommended to use OAuth credentials as well and store them in the credential store with the key name `external` as such ``auth session --store-key external --creds PATH_TO_CREDS``.
- It is recommended to have all Google Chrome profiles established and pre-authenticated for users where OAuth credentials are used. This will be useful when the OAuth consent screen appears and the user can select the appropriate profile to authenticate with.
- It is recommended to keep the `store_on_exit` value in the `etc/config.yaml` to `True` to ensure credentials are stored and available for future use.
- Most OOTB emulations require 1-2 users with OAuth creds to emulate either internal or external user activity.


Conclusion
----------

The foundation of SWAT's integration with Google Workspace is its structured handling of authentication. By using dataclasses for structured credential representation and offering a dedicated credential store, SWAT ensures secure and efficient authentication and authorization flows.
