from commands.base_command import BaseCommand

class Command(BaseCommand):
    def __init__(self, args):
        super().__init__(args)

    def execute(self):
        print("hello world")