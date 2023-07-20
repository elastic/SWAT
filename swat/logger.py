
import logging


def configure_logging(config: dict = None, level: int = logging.INFO) -> None:
    """Logging for the entire application."""
    # Set up logging format
    log_file_format = config['logging']['log_file_format']
    log_console_format = config['logging']['log_console_format']

    # Set up console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(logging.Formatter(log_console_format))

    # Set up file handler
    log_file = config['logging']['path']
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level)
    file_handler.setFormatter(logging.Formatter(log_file_format))

    # Add handlers to the root logger
    logger = logging.getLogger()
    logger.setLevel(level)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
