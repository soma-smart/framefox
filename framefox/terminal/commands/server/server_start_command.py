import subprocess

from framefox.terminal.commands.abstract_command import AbstractCommand


class ServerStartCommand(AbstractCommand):
    def __init__(self):
        super().__init__("start")

    def execute(self, port: int = 8000):
        """
        Run a server using Uvicorn with the reload option.
        """
        subprocess.run(["uvicorn", "main:app", "--reload", "--port", str(port)])
