
from swat.commands.base_command import BaseCommand


class Command(BaseCommand):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def execute(self) -> None:
        print("hello world")
