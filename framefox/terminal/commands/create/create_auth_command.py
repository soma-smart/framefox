from framefox.terminal.commands.abstract_command import AbstractCommand


class CreateAuthCommand(AbstractCommand):
    def __init__(self):
        super().__init__('auth')

    def execute(self):
        print("Hello from CreateAuthCommand")
