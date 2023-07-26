
import logging
from typing import List

from ..base import SWAT


class BaseCommand:
    def __init__(self, command: str = None, args: List[str] = list, obj: SWAT = None) -> None:
        self.command = command
        self.args = args
        self.logger = logging.getLogger(__name__)
        self.obj = obj

    def execute(self) -> None:
        raise NotImplementedError("The 'execute' method must be implemented in each command class.")
