class BaseCommand:
    def __init__(self, args):
        self.args = args

    def execute(self):
        raise NotImplementedError("The 'execute' method must be implemented in each command class.")
