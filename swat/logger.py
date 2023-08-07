import logging
from pathlib import Path
from colorama import Fore, Style, init
import os

DEFAULT_LOGGING_PATH = Path.cwd() / 'logs'
init(autoreset=True)  # Automatically reset color after each print

def configure_logging(config: dict = None, level: int = logging.INFO) -> None:
    '''Logging for the entire application.'''
    log_file_format = config['logging']['log_file_format']
    log_console_format = config['logging']['log_console_format']

    class CustomFormatter(logging.Formatter):
        def format(self, record):
            timestamp_format = '%Y-%m-%d %H:%M:%S'
            timestamp = self.formatTime(record, timestamp_format)
            colored_timestamp = Fore.BLUE + timestamp + Style.RESET_ALL

            colored_message = Fore.GREEN + str(record.msg) + Style.RESET_ALL

            file_name = os.path.basename(record.pathname)
            colored_file_name = Fore.RED + file_name + Style.RESET_ALL
            colored_line_number = Fore.BLUE + str(record.lineno) + Style.RESET_ALL

            file_info = f"{record.funcName}:{colored_file_name}:{colored_line_number}"
            colored_file_info = Fore.YELLOW + f"({file_info})" + Style.RESET_ALL

            log_message = f"{colored_timestamp} {record.levelname} {colored_message} {colored_file_info}"
            return log_message

    # Set up console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(CustomFormatter(log_console_format))

    # Set up file handler
    DEFAULT_LOGGING_PATH.mkdir(exist_ok=True)
    log_file = DEFAULT_LOGGING_PATH / 'swat.log'
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level)
    file_handler.setFormatter(logging.Formatter(log_file_format))

    # Add handlers to the root logger
    logger = logging.getLogger()
    logger.setLevel(level)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

def configure_emulation_logger(emulation_name: str, config: dict, level: int = logging.INFO) -> logging.Logger:
    '''Logging for a specific emulation.'''
    elogger = logging.getLogger(f'{emulation_name}')

    # Ensure 'logs' directory exists
    DEFAULT_LOGGING_PATH.mkdir(exist_ok=True)

    # Create file handler for the emulation-specific log file
    tactic, playbook = emulation_name.split('.')
    log_file = DEFAULT_LOGGING_PATH / f'{tactic}_{playbook}.log'
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level)
    log_file_format = config['logging']['log_file_format']
    file_handler.setFormatter(logging.Formatter(log_file_format))

    # Add the file handler to the emulation logger
    elogger.addHandler(file_handler)

    return elogger