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

    required_attributes = [
        ("name", "has no name defined"),
        ("parser", "has no parser defined"),
        ("services", "has no services defined"),
        ("scopes", "has no scopes defined"),
        ("techniques", "has no techniques defined"),
        ("execute", "has no execute method defined"),
    ]

    @pytest.mark.parametrize("emulation", emulations_list, ids=lambda e: e.name)
    @pytest.mark.parametrize("attribute, error_msg", required_attributes)
    def test_required_attributes(self, emulation: Type[BaseEmulation], attribute: str, error_msg: str):
        """Test if required attributes are defined in emulation."""

        assert hasattr(emulation, attribute), f'Emulation "{emulation.name}" {error_msg}'