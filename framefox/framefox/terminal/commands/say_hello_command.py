from framefox.terminal.commands.abstract_command import AbstractCommand


class SayHelloCommand(AbstractCommand):
    def __init__(self):
        super().__init__('say_hello')

    def execute(self, name: str):
        """
        Toto
        """
        print(f"Welcome {name}")
