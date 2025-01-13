from framefox.terminal.argument_parser import ArgumentParser
from framefox.terminal.command_handler import CommandHandler


class Terminal:

    def __init__(self):
        self.arg_parser = ArgumentParser()
        self.command_handler = CommandHandler()
        self.command_handler.load_commands()

    def run(self):
        self.command_handler.run(
            self.arg_parser.get_command(), self.arg_parser.get_args()
        )
