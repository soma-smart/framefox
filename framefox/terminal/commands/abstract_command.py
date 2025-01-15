from framefox.terminal.common.printer import Printer


class AbstractCommand:
    def __init__(self, name):
        self.name = name
        self.printer = Printer()

    def execute(self, *args):
        raise NotImplementedError("Subclasses must implement this method")
