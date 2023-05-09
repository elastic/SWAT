
from swat.commands.base_command import BaseCommand


class Command(BaseCommand):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        assert len(self.args) > 0, "No emulation command provided."
        self.emulation_command, *self.args = self.args

    def execute(self) -> None:
        if self.emulation_command == "hello":
            print(f"hello {' '.join(self.args)}")
