import signal
import subprocess
import sys
import time

from framefox.terminal.commands.abstract_command import AbstractCommand


class ServerStartCommand(AbstractCommand):
    def __init__(self):
        super().__init__("server:start")
        self.process = None
        self.running = True

    def execute(self, port: int = 8000, *args, **kwargs):
        """
        Start the uvicorn server.
        """
        self.printer.print_msg(
            f"Starting the server on port {port}",
            theme="success",
            linebefore=True,
        )

        self._setup_signal_handlers()

        try:
            self.process = subprocess.Popen(
                ["uvicorn", "main:app", "--reload", "--port", str(port)],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
            )

            while self.running and self.process.poll() is None:
                line = self.process.stdout.readline().rstrip()
                if line:
                    print(line)
                time.sleep(0.1)

            if self.process.poll() is None:
                self._graceful_shutdown()

            return 0
        except KeyboardInterrupt:
            self._graceful_shutdown()
            return 0

    def _setup_signal_handlers(self):
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, sig, frame):
        self.printer.print_msg("\nStopping the server...", theme="warning")
        self.running = False

    def _graceful_shutdown(self):
        if self.process and self.process.poll() is None:
            self.process.send_signal(signal.SIGINT)

            try:
                self.process.wait(timeout=5)
                self.printer.print_msg("Server stopped successfully", theme="success")
            except subprocess.TimeoutExpired:
                self.printer.print_msg(
                    "Timeout exceeded, forcing server shutdown", theme="warning"
                )
                self.process.terminate()
                try:
                    self.process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    self.process.kill()
                    self.printer.print_msg("Server forcibly terminated", theme="error")
