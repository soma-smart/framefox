import subprocess

from framefox.terminal.commands.abstract_command import AbstractCommand


class ServerStartCommand(AbstractCommand):
    def execute(self, port: int = 8000, *args, **kwargs):
        """
        Démarre le serveur de développement avec Uvicorn
        """
        self.printer.print_msg(
            f"Starting server on port {port}",
            theme="success",
            linebefore=True,
        )

        subprocess.run(["uvicorn", "main:app", "--reload", "--port", str(port)])

        return 0
