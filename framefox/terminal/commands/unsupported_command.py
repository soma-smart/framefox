from framefox.terminal.commands.abstract_command import AbstractCommand

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: LEUROND Raphaël
Github: https://github.com/Vasulvius
"""


class UnsupportedCommand(AbstractCommand):
    """
    This is a special class for unsupported commands.
    """

    def __init__(self):
        super().__init__("unsupported")

    def execute(self, *args):
        """
        Executes the unsupported command.
        """
        print("Unsupported command.")
