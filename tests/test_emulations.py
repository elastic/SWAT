import warnings
from typing import List, Type

import pytest

from swat.commands.base_command import BaseCommand
from swat.commands.emulate import Command as emulate_command
from swat.emulations.base_emulation import BaseEmulation


class TestEmulations:
    """Test class for emulations."""

    @staticmethod
    def get_all_emulation_classes() -> List[Type[BaseEmulation]]:
        """Fetch all emulation classes."""

        return emulate_command().load_all_emulation_classes()

    emulations_list = get_all_emulation_classes.__func__()

    @pytest.mark.parametrize("emulation", emulations_list, ids=lambda e: e.name)
    def test_inheritance(self, emulation: Type[BaseEmulation]):
        """Test if emulation inherits from BaseEmulation."""
        assert issubclass(emulation, BaseEmulation), f'Emulation "{emulation.name}" does not inherit from BaseEmulation'

    @pytest.mark.parametrize("emulation", emulations_list, ids=lambda e: e.name)
    def test_parser_defined(self, emulation: Type[BaseEmulation]):
        """Test if parser is defined in emulation."""
        assert hasattr(emulation, 'parser'), f'Emulation "{emulation.name}" has no parser defined'

    @pytest.mark.parametrize("emulation", emulations_list, ids=lambda e: e.name)
    def test_services_defined(self, emulation: Type[BaseEmulation]):
        """Test if services are defined in emulation."""
        assert hasattr(emulation, 'services'), f'Emulation "{emulation.name}" has no services defined'

    @pytest.mark.parametrize("emulation", emulations_list, ids=lambda e: e.name)
    def test_scopes_defined(self, emulation: Type[BaseEmulation]):
        """Test if scopes are defined in emulation."""
        assert hasattr(emulation, 'scopes'), f'Emulation "{emulation.name}" has no scopes defined'

    @pytest.mark.parametrize("emulation", emulations_list, ids=lambda e: e.name)
    def test_techniques_defined(self, emulation: Type[BaseEmulation]):
        """Test if techniques are defined in emulation."""
        assert hasattr(emulation, 'techniques'), f'Emulation "{emulation.name}" has no techniques defined'

    @pytest.mark.parametrize("emulation", emulations_list, ids=lambda e: e.name)
    def test_execute_method_defined(self, emulation: Type[BaseEmulation]):
        """Test if execute method is defined in emulation."""
        assert hasattr(emulation, 'execute'), f'Emulation "{emulation.name}" has no execute method defined'
