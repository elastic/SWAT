from .swat.commands.base_command import BaseCommand


class Command(BaseCommand):
    def __init__(self, args: str) -> None:
        super().__init__(args)

    def execute(self) -> None:
        print("hello world")