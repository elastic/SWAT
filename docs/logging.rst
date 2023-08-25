Logging
=======

SWAT has a simply designed logging and output mechanism, ensuring that users and developers alike have clear insights into its operations. Not only does this feature provide valuable feedback, but it also introduces a touch of humor with its color patterns!

Logging module
--------------

This module provides the foundational tools for setting up and managing the SWAT project's logging mechanism. It encompasses both application-wide and emulation-specific logging.

1. **Global Application Logging**: Defined in the `configure_logging` function, this segment of the module pertains to logging across the entire application. Notably, the `CustomFormatter` class within this function is pivotal in customizing the log format. It assigns various colors to different segments of the log for easy differentiation and readability.

   Colors used include:

   - Timestamp: Blue
   - Log Message: Green
   - File Name: Red
   - Line Number: Blue
   - File Info (Function Name, File Name, Line Number): Yellow

2. **Emulation-Specific Logging**: Defined in the `configure_emulation_logger` function, this feature caters exclusively to emulation activities. Logging for each emulation is separately maintained, with each emulation having its distinct log file named according to its tactic and playbook.

The module also makes proactive efforts to ensure the presence of the necessary directory for storing logs. The use of the `colorama` library ensures that logging remains visually engaging and easily distinguishable in the console.

Setup and Configuration
-----------------------

SWAT's logging is primarily based on the foundational `BaseCommand` class. Every command in SWAT, by virtue of inheriting from this class, gets immediate access to the built-in logging functionality:

1. **BaseCommand's Logger**: The `BaseCommand` class initializes a global logger, `self.logger`. This logger is thereby inherited by any class extending `BaseCommand`.

2. **BaseEmulation's Logger**: In addition to the global logger from `BaseCommand`, the `BaseEmulation` class sets up a specialized logger, `self.elogger`. This logger is primarily intended for emulations, allowing for a separate log file tailored for emulation activities. The logger is subsequently available to any class extending `BaseEmulation`.

Usage in Commands and Emulations
--------------------------------

1. **General Logging**: Due to the inheritance from `BaseCommand`, all command classes have access to the `self.logger` instance. This can be seen in both `auth.py` and `emulate.py`.

   .. code-block:: python

      self.logger.info('This is a general informational message.')

2. **Emulation-Specific Logging**: Emulations, on the other hand, can use both the global logger and the emulation-specific logger:

   .. code-block:: python

      self.logger.info('General log message.')
      self.elogger.info('Emulation-specific log message.')

Colors and Humor
----------------

The color patterns of SWAT's logging are inspired by Google. Why? Well, why not? It's always refreshing to add a bit of flair and humor to the mix!

Logging Philosophy
------------------

1. **Consistent Feedback**: All output in the shell is channeled through the console logger handlers. This ensures consistency in feedback without relying on disparate print statements.

2. **Avoid Direct Printing**: While there might be occasions where direct printing is tempting, the emphasis is on using the logger for output. It keeps the feedback uniform, structured, and traceable.

Conclusion
----------

SWAT's logging is a mix of functionality, clarity, and humor. It's designed not just for transparency and traceability, but also for user delight. The dual logging mechanism — one for general commands and another specifically tailored for emulations — ensures that every aspect of the project has detailed logging coverage, catering to both broad and specific use cases.
