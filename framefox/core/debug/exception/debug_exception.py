class DebugException(Exception):
    def __init__(self, content: str):
        self.content = content
