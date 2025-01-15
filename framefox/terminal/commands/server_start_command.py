from framefox.terminal.commands.abstract_command import AbstractCommand
import subprocess


class ServerStartCommand(AbstractCommand):
    def __init__(self):
        super().__init__('server_start')

    def execute(self):
        """
        Run a server using Uvicorn with the reload option.
        """
        subprocess.run(["uvicorn", "main:app", "--reload"])
