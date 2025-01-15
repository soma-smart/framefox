class AbstractCommand:
    def __init__(self, name):
        self.name = name

    def execute(self, *args):
        raise NotImplementedError("Subclasses must implement this method")
