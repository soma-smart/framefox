from src.terminal.commands.abstract_command import AbstractCommand


class UnsupportedCommand(AbstractCommand):
    def __init__(self):
        super().__init__('unsupported')

    def execute(self, *args):
        print("Unsupported command.")
