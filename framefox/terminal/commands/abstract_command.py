from framefox.terminal.common.printer import Printer

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: LEUROND Raphaël
Github: https://github.com/Vasulvius
"""


class AbstractCommand:
    def __init__(self, name):
        self.name = name
        self.printer = Printer()

    def execute(self, *args):
        raise NotImplementedError("Subclasses must implement this method")
