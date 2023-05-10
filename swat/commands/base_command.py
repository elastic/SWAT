
from typing import List


class BaseCommand:
    def __init__(self, command: str, args: List[str], config: dict, **auth) -> None:
        self.command = command
        self.args = args
        self.auth = auth
        self.config = config

    def execute(self) -> None:
        raise NotImplementedError("The 'execute' method must be implemented in each command class.")
