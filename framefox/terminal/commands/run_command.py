import os
import socket
import subprocess
import threading
import time
import webbrowser
from typing import Annotated

import typer

from framefox.terminal.commands.abstract_command import AbstractCommand

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen & LEUROND Raphael
Github: https://github.com/RayenBou
Github: https://github.com/Vasulvius
"""


class RunCommand(AbstractCommand):
    """
    Command to start the development server with optimizations.

    This command handles starting a uvicorn server with automatic port detection,
    container pre-warming, and automatic browser opening.
    """

    BROWSER_DELAY_SECONDS = 2
    MAX_PORT_SEARCH_ATTEMPTS = 10

    def __init__(self):
        """Initialize the run command."""
        super().__init__("run")

    def execute(
        self,
        port: Annotated[int, typer.Option("--port", "-p", help="Port to run the server on")] = 8000,
        no_browser: Annotated[bool, typer.Option("--no-browser", help="Don't open browser automatically")] = False,
    ):
        """
        Run the development server
        Args:
            port (int): The port to run the server on. Defaults to 8000.

            no_browser (bool): Whether to skip opening the browser automatically. Defaults to False.
        """
        os.environ["FRAMEFOX_DEV_MODE"] = "true"
        os.environ["FRAMEFOX_CACHE_ENABLED"] = "true"
        os.environ["FRAMEFOX_MINIMAL_SCAN"] = "true"

        available_port = self._find_available_port(port)

        self.printer.print_msg(
            f"Starting optimized dev server on port {available_port}",
            theme="success",
            linebefore=True,
        )

        self._handle_browser_opening(available_port, no_browser)
        return self._start_uvicorn_server(available_port)

    def _find_available_port(self, initial_port: int) -> int:
        current_port = initial_port

        while self._is_port_in_use(current_port) and current_port < initial_port + self.MAX_PORT_SEARCH_ATTEMPTS:
            self.printer.print_msg(
                f"Port {current_port} already in use, trying {current_port + 1}...",
                theme="warning",
            )
            current_port += 1

        return current_port

    def _handle_browser_opening(self, port: int, no_browser: bool):
        server_url = f"http://localhost:{port}"

        if not no_browser:
            browser_thread = threading.Thread(target=self._open_browser_delayed, args=(server_url,), daemon=True)
            browser_thread.start()
        else:
            self.printer.print_msg(
                f"Server will be available at {server_url}",
                theme="info",
            )

    def _start_uvicorn_server(self, port: int) -> int:
        try:
            uvicorn_cmd = [
                "uvicorn",
                "main:app",
                "--reload",
                "--reload-delay",
                "0.5",
                "--reload-dir",
                "src",
                "--port",
                str(port),
            ]

            process = subprocess.run(uvicorn_cmd)
            return process.returncode

        except KeyboardInterrupt:
            self.printer.print_msg("\nStopping the server...", theme="warning")
            return 0

    def _is_port_in_use(self, port: int) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(("localhost", port)) == 0

    def _open_browser_delayed(self, url: str):
        time.sleep(self.BROWSER_DELAY_SECONDS)
        webbrowser.open(url)
