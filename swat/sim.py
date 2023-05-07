from swat.commands.base_command import BaseCommand
import dataclasses
import typing

class Command(BaseCommand):
    def __init__(self, args):
        super().__init__(args)

    def execute(self):
        print("hello world")