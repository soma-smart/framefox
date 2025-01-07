from src.terminal.commands.abstract_command import AbstractCommand


class CreateFileCommand(AbstractCommand):
    """
    Test command to create a file.
    """

    def __init__(self):
        super().__init__('say_hello')

    def execute(self, arg1, agr2):
        """
        Execute the command to say hello.

        Args:
            arg1 (str): The first argument.
            agr2 (str): The second argument.
        """
        print(f"Hello : {arg1} {agr2}")
