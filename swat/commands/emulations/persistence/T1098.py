
from swat.commands.emulate import BaseEmulationCommand


class Command(BaseEmulationCommand):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def execute(self) -> None:
        print("hello world")
