
import argparse
from pathlib import Path

import yaml


DEFAULT_CONFIG = Path(__file__).parent.parent / "etc" / "config.yaml"


class CustomHelpFormatter(argparse.HelpFormatter):
    """Override the default help formatter to exclude usage."""

    def add_usage(self, usage, actions, groups, prefix=None):
        # Do nothing, effectively skipping usage output
        pass


def get_custom_argparse_formatter(*args, **kwargs) -> argparse.ArgumentParser:
    assert "description" in kwargs, "Must provide 'description' argument."
    return argparse.ArgumentParser(formatter_class=CustomHelpFormatter, add_help=False, *args, **kwargs)


def validate_args(parser: argparse.ArgumentParser, args: list[str]):
    """Parse arguments."""
    try:
        parsed_args, unknown = parser.parse_known_args(args)
        if unknown:
            raise ValueError(f"Unknown arguments {unknown}")
    except SystemExit:
        raise ValueError(parser.format_help())
    return parsed_args


def default_config():
    return yaml.safe_load(DEFAULT_CONFIG.read_text())
