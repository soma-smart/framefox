from src.terminal.commands.abstract_command import AbstractCommand


class CreateFileCommand(AbstractCommand):
    def __init__(self):
        super().__init__('say_hello')

    def execute(self, arg1, agr2):
        print(f"Hello : {arg1} {agr2}")
