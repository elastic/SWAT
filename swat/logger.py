
import logging
from pathlib import Path

from colorama import Fore, Style

DEFAULT_LOGGING_PATH = Path.cwd() / "logs"

def configure_logging(config: dict = None, level: int = logging.INFO) -> None:
    """Logging for the entire application."""
    # Set up logging format
    log_file_format = config['logging']['log_file_format']
    log_console_format = config['logging']['log_console_format']

    class CustomFormatter(logging.Formatter):

        def format(self, record):
            colors = {
                logging.DEBUG: Style.RESET_ALL,
                logging.INFO: Fore.CYAN,
                logging.WARNING: Fore.YELLOW,
                logging.ERROR: Fore.RED,
                logging.CRITICAL: Fore.LIGHTRED_EX
            }
            log_fmt = f'{colors.get(record.levelno)} {log_console_format} {Style.RESET_ALL}'
            formatter = logging.Formatter(log_fmt)
            return formatter.format(record)


    # Set up console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(CustomFormatter())

    # Set up file handler
    DEFAULT_LOGGING_PATH .mkdir(exist_ok=True)
    log_file = DEFAULT_LOGGING_PATH / "swat.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level)
    file_handler.setFormatter(logging.Formatter(log_file_format))

    # Add handlers to the root logger
    logger = logging.getLogger()
    logger.setLevel(level)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

def configure_emulation_logger(emulation_name: str, config: dict, level: int = logging.INFO) -> logging.Logger:
    """Logging for a specific emulation."""
    elogger = logging.getLogger(f"{emulation_name}")

    # Ensure 'logs' directory exists
    DEFAULT_LOGGING_PATH.mkdir(exist_ok=True)

    # Create file handler for the emulation-specific log file
    tactic, playbook = emulation_name.split('.')
    log_file = DEFAULT_LOGGING_PATH / f"{tactic}_{playbook}.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level)
    log_file_format = config['logging']['log_file_format']
    file_handler.setFormatter(logging.Formatter(log_file_format))

    # Add the file handler to the emulation logger
    elogger.addHandler(file_handler)

    return elogger