import argparse

import yaml


class CustomHelpFormatter(argparse.HelpFormatter):
    """Override the default help formatter to exclude usage."""

    def add_usage(self, usage, actions, groups, prefix=None):
        # Do nothing, effectively skipping usage output
        pass


def get_custom_argparse_formatter(*args, **kwargs) -> argparse.ArgumentParser:
    assert "description" in kwargs and "prog" in kwargs, "Must provide 'description' and 'prog' arguments."
    return argparse.ArgumentParser(formatter_class=CustomHelpFormatter, add_help=False, *args, **kwargs)


def validate_args(parser, args):
    """Parse arguments."""
    try:
        parsed_args, unknown = parser.parse_known_args(args)
        if unknown:
            raise ValueError(f"Unknown arguments {unknown}")
    except SystemExit:
        return None
    return parsed_args


def default_config():
    with open('swat/etc/config.yaml', 'r') as file:
        return yaml.safe_load(file)