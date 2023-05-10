import logging
from pathlib import Path
from typing import List

import yaml

from typing import List


class BaseCommand:
    def __init__(self, command: str = None, args: List[str] = [], credentials: Path = None,
                 token: Path = None, config: dict = None) -> None:
        self.command = command
        self.args = args
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.credentials = credentials
        self.token = token


    def execute(self) -> None:
        raise NotImplementedError("The 'execute' method must be implemented in each command class.")
