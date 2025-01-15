from framefox.terminal.commands.abstract_command import AbstractCommand


class HelloWorldCommand(AbstractCommand):
    def __init__(self):
        super().__init__('hello_world')

    def execute(self):
        """
        Print "Hello World!" to the console.
        """
        print("Hello World!")
