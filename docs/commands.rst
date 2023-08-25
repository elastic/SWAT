Commands
========

SWAT (Simple Workspace ATT&CK Tool) is a modular and dynamic command-line tool that allows for the execution of various commands. This guide will dive into the structure of SWAT commands, explain how they work, and guide you through adding new commands to expand its functionality.

Prerequisites
-------------

Before you dive into adding commands to SWAT, ensure you have:

- Familiarity with the `argparse` module in Python.
- Basic understanding of the SWAT architecture, especially `base_command.py` and `shell.py`.
- Necessary API credentials or configurations for any external service your command will be integrating with, like the Google Workspace Admin API in our example.

Understanding the BaseCommand Class
-----------------------------------

The `BaseCommand` class serves as the foundation for all SWAT commands. Beyond providing a consistent interface for commands, it offers:

- Logging capabilities: This ensures all commands have access to the same logging setup and formats.
- Argparse configurations: Allows commands to easily integrate with SWAT's command-line interface.
- (Any other functionality provided by the `BaseCommand` that might be relevant but hasn't been highlighted).

Understanding Commands
----------------------

BaseCommand Inheritance
-----------------------

All commands in SWAT inherit from the ``BaseCommand`` class in ``swat/base_command.py``, allowing for a consistent interface and shared functionalities. This allows different SWAT commands and emulations to inherit the base ``SWAT`` object from ``base.py``, as well as the logging capability, commands, and arguments.

Command Structure
-----------------

A typical SWAT command class contains:

Command Class
^^^^^^^^^^^^^

Commands have a single ``Command(BaseCommand)`` class that inherits from ``BaseCommand`` the global SWAT object, logger handles, arguments, commands, and more.

Commands use argparse to define their command-line interface. In addition to the main parser, they may also define subparsers for different subcommands, with specific arguments and options for each:

.. code-block:: python

   class Command(BaseCommand):
       parser = BaseCommand.load_parser(description='Description here')
       subparsers = parser.add_subparsers(dest='subcommand', title='subcommands', required=True)

       parser_session = subparsers.add_parser('session', description='Description for session')
       # Add arguments and options for the 'session' subcommand

Initialization Method
^^^^^^^^^^^^^^^^^^^^^

Commands in SWAT generally require an initialization method, where they set up specific parser settings, defaults, and validate arguments:

.. code-block:: python

   def __init__(self, **kwargs) -> None:
       super().__init__(**kwargs)
       self.parser_session.set_defaults(func=self.authenticate)
       self.parser_list.set_defaults(func=self.list_sessions)

       self.args = validate_args(self.parser, self.args)

Execute Method
^^^^^^^^^^^^^^

The required method that gets called when the command is executed:

.. code-block:: python

   def execute(self) -> None:
       # Main command logic

Dynamic Loading
---------------

Commands are dynamically loaded from the ``swat/commands/`` directory, enabling SWAT to import and execute them at runtime.

Command Execution Workflow
^^^^^^^^^^^^^^^^^^^^^^^^^^

1. Pre-Command Processing: Extract command name and arguments.
2. Loading Command: Dynamically load the command class.
3. Instantiate Command: Create an instance of the command class.
4. Execute Command: Call the command's ``execute()`` method.
5. Post-Command Processing: Handle any necessary post-execution steps.

Error Handling and Logging
--------------------------

SWAT commands come with built-in logging capabilities, inherited from the `BaseCommand` class. When developing your command, consider the following:

- Log meaningful information, especially potential errors or exceptions.
- Always handle exceptions with try-except blocks to prevent the entire tool from crashing due to command errors.
- Ensure logging levels are appropriately set (e.g., debug, info, warning, error).

Adding a New Command
--------------------

SWAT is designed to simplify the process of adding new commands. However, to make things clearer, we'll walk through an example of adding a command called ``users``, which interacts with the Google Workspace Admin API to retrieve details about existing Google Workspace users.

.. code-block:: python
   :caption: Full command code example
   :name: Full command code example

   from googleapiclient.discovery import build
   from ..commands.base_command import BaseCommand
   from ..misc import validate_args

   class Command(BaseCommand):

       parser = BaseCommand.load_parser(description='Interact with Google Workspace Users.')
       subparsers = parser.add_subparsers(dest='subcommand', title='subcommands', required=True)

       parser_list = subparsers.add_parser('list', description='List all users in the domain')

       parser_view = subparsers.add_parser('view', description='View details of a specific user')
       parser_view.add_argument('user_id', help='The unique ID or email of the user')

       def __init__(self, **kwargs) -> None:
           super().__init__(**kwargs)
           self.parser_list.set_defaults(func=self.list_users)
           self.parser_view.set_defaults(func=self.view_user)

           self.args = validate_args(self.parser, self.args)

       def list_users(self):
           '''List all users in the Google Workspace domain.'''
           service = build('admin', 'directory_v1', credentials=self.obj.cred_store.store['default'].session)
           results = service.users().list(domain=self.obj.config['google']['domain']).execute()
           users = results.get('users', [])
           for user in users:
               self.logger.info(user['primaryEmail'])

       def view_user(self):
           '''View details of a specific user.'''
           service = build('admin', 'directory_v1', credentials=self.obj.credentials)
           user = service.users().get(userKey=self.args.user_id).execute()
           self.logger.info(user)

       def execute(self) -> None:
           '''Main execution method.'''
           self.args.func()

Example Walkthrough:
^^^^^^^^^^^^^^^^^^^^

1. **Create a new file**: In the SWAT directory, create a file named ``users.py`` inside the ``swat/commands/`` directory.

   .. code-block:: bash

      touch swat/commands/users.py

2. **Add necessary imports**: Ensure you have the following imports at the beginning of the `users.py` file. Remember that ``BaseCommand`` and ``validate_args`` are crucial for inheritance and argparse.

   .. code-block:: python

      from googleapiclient.discovery import build
      from ..commands.base_command import BaseCommand
      from ..misc import validate_args

3. **Define the Command Class**: Start by defining the `Command(BaseCommand)` class.

   .. code-block:: python

      class Command(BaseCommand):
          ...

4. **Initialization Method**: Add the `__init__` method that inherits from `BaseCommand` and validates the arguments for the `users` command. You should also set up the `self.service` variable that facilitates access to the Admin API. For authentication details, refer to the `How-To: Authenticate with OAuth <https://github.com/elastic/SWAT/wiki/How%E2%80%90To#oauth>`_ section.

   .. code-block:: python

      def __init__(self, **kwargs) -> None:
          ...

5. **Execution Method**: Add the `execute()` method, which essentially invokes `self.args.func()`.

   .. code-block:: python

      def execute(self) -> None:
          ...

6. **Set up Argparse**: Implement argparse subcommands and parsers. In this example, the `users` command has `list` and `view` as subcommands. Additionally, the `view` command requires the `user_id` argument.

   .. code-block:: python

      parser = BaseCommand.load_parser(description='Interact with Google Workspace Users.')
      subparsers = parser.add_subparsers(dest='subcommand', title='subcommands', required=True)
      ...

7. **Implement Command Logic**: Write methods that define the functionalities of the command.

   .. code-block:: python

      def list_users(self):
          ...

      def view_user(self):
          ...

8. **Test Your Command**: Start SWAT and execute the help command to ensure everything is working as expected.

   .. code-block:: bash

      help users
