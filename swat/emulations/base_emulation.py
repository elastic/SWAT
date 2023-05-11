import logging
from pathlib import Path


class BaseEmulation:
    def __init__(self, tactic: str, technique: str, credentials: Path = None,
                 token: Path = None, config: dict = None) -> None:
        self.tactic = tactic
        self.technique = technique
        self.config = config
        self.credentials = credentials
        self.token = token
        self.logger = logging.getLogger(__name__)

    def execute(self) -> None:
        raise NotImplementedError("The 'execute' method must be implemented in each emulation class.")
