import warnings

import pytest

from swat.commands.base_command import BaseCommand
from swat.commands.emulate import Command as emulate_command
from swat.emulations.base_emulation import BaseEmulation


class TestEmulations:
    """Tests for emulations."""

    @pytest.fixture(scope="class", autouse=True)
    def emulations(self):
        return emulate_command().load_all_emulation_classes()

    def test_techniques(self, emulations):
        errors = [f'Emulation "{emulation.name}" has no techniques defined' for emulation in emulations if not hasattr(emulation, 'techniques')]
        assert not errors, '\n'.join(errors)

    def test_services(self, emulations):
        errors = [f'Emulation "{emulation.name}" has no services defined' for emulation in emulations if not hasattr(emulation, 'services')]
        assert not errors, '\n'.join(errors)

    def test_name(self, emulations):
        errors = [f'Emulation "{emulation}" has no name defined' for emulation in emulations if not hasattr(emulation, 'name')]
        assert not errors, '\n'.join(errors)

    def test_scopes(self, emulations):
        errors = [f'Emulation "{emulation.name}" has no scopes defined' for emulation in emulations if not hasattr(emulation, 'scopes')]
        assert not errors, '\n'.join(errors)

    def test_parser(self, emulations):
        errors = [f'Emulation "{emulation.name}" has no parser defined' for emulation in emulations if not hasattr(emulation, 'parser')]
        assert not errors, '\n'.join(errors)

    def test_execute(self, emulations):
        errors = [f'Emulation "{emulation.name}" has no execute method defined' for emulation in emulations if not hasattr(emulation, 'execute')]
        assert not errors, '\n'.join(errors)

    def test_cleanup(self, emulations):
        warn_msgs = [f'Emulation "{emulation.__module__}" has no cleanup method defined' for emulation in emulations if not hasattr(emulation, 'cleanup')]
        for msg in warn_msgs:
            warnings.warn(msg)
