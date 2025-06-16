import asyncio
import os
import socket
import subprocess
import threading
import time
import webbrowser
from typing import Annotated

import typer

from framefox.core.di.service_container import ServiceContainer
from framefox.terminal.commands.abstract_command import AbstractCommand

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class RunCommand(AbstractCommand):
    """
    Command to start the development server with optimizations.

    This command handles starting a uvicorn server with automatic port detection,
    container pre-warming, optional background workers, and automatic browser opening.
    """

    BROWSER_DELAY_SECONDS = 2
    MAX_PORT_SEARCH_ATTEMPTS = 10
    WORKER_SHUTDOWN_TIMEOUT = 2.0

    def __init__(self):
        """Initialize the run command."""
        super().__init__("run")
        self.worker_thread = None
        self.worker_stop_event = None

    def execute(
        self,
        port: Annotated[int, typer.Option("--port", "-p", help="Port to run the server on")] = 8000,
        with_workers: Annotated[bool, typer.Option("--with-workers", help="Start background workers")] = False,
        no_browser: Annotated[bool, typer.Option("--no-browser", help="Don't open browser automatically")] = False,
    ):
        """
        Execute the run command to start the development server.\n
        This method performs the following steps:\n
        1. Set environment variables for development mode and caching.\n
        2. Find an available port starting from the specified port.\n
        3. Prewarm the service container to optimize startup performance.\n
        4. Print a success message with the server URL.\n
        5. Optionally set up background workers for asynchronous tasks.\n
        6. Handle browser opening based on user preference.\n
        7. Start the uvicorn server with the specified port and options.\n
        Args:
            port (int): The port to run the server on. Defaults to 8000.
            with_workers (bool): Whether to start background workers. Defaults to False.
            no_browser (bool): Whether to skip opening the browser automatically. Defaults to False.
        """
        os.environ["FRAMEFOX_DEV_MODE"] = "true"
        os.environ["FRAMEFOX_CACHE_ENABLED"] = "true"
        os.environ["FRAMEFOX_MINIMAL_SCAN"] = "true"

        available_port = self._find_available_port(port)
        self._prewarm_container()

        self.printer.print_msg(
            f"Starting optimized dev server on port {available_port}",
            theme="success",
            linebefore=True,
        )

        if with_workers:
            self._setup_workers()

        self._handle_browser_opening(available_port, no_browser)
        return self._start_uvicorn_server(available_port)

    def _find_available_port(self, initial_port: int) -> int:
        current_port = initial_port

        while self._is_port_in_use(current_port) and current_port < initial_port + self.MAX_PORT_SEARCH_ATTEMPTS:
            self.printer.print_msg(f"Port {current_port} already in use, trying {current_port + 1}...", theme="warning")
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
            uvicorn_cmd = ["uvicorn", "main:app", "--reload", "--reload-delay", "0.5", "--reload-dir", "src", "--port", str(port)]

            process = subprocess.run(uvicorn_cmd)
            return process.returncode

        except KeyboardInterrupt:
            self.printer.print_msg("\nStopping the server...", theme="warning")
            self._cleanup_workers()
            return 0

    def _prewarm_container(self) -> None:
        """Prewarm the service container for better startup performance."""
        try:
            container = ServiceContainer()
            container.force_complete_scan()

            cache_data = container._create_cache_snapshot()
            container._save_service_cache(cache_data)

        except Exception as e:
            self.printer.print_msg(f"⚠️ Pre-warm failed: {e}", theme="warning")

    def _cleanup_workers(self):
        if self.worker_stop_event:
            self.worker_stop_event.set()

        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=self.WORKER_SHUTDOWN_TIMEOUT)

            if self.worker_thread.is_alive():
                self.printer.print_msg("Warning: Worker thread did not shut down gracefully", theme="warning")

    def _is_port_in_use(self, port: int) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(("localhost", port)) == 0

    def _open_browser_delayed(self, url: str):
        time.sleep(self.BROWSER_DELAY_SECONDS)
        webbrowser.open(url)

    def _setup_workers(self):
        """
        Set up background worker thread for processing asynchronous tasks.

        This creates a separate thread that runs an asyncio event loop
        for handling background tasks like queue processing, scheduled jobs, etc.
        """
        self.printer.print_msg(
            "Starting worker process in background...",
            theme="info",
            linebefore=True,
        )
        try:
            self.worker_stop_event = threading.Event()
            self.worker_thread = threading.Thread(target=self._run_worker_thread, daemon=True, name="FramefoxWorker")
            self.worker_thread.start()
        except Exception as e:
            self.printer.print_msg(f"Failed to start worker: {str(e)}", theme="error")

    def _run_worker_thread(self):
        """
        Execute the worker manager in a separate thread with its own event loop.

        This method:
        1. Creates a new asyncio event loop for the worker thread
        2. Starts the worker manager's processing loop
        3. Monitors for shutdown signals
        4. Handles graceful shutdown when requested
        """
        try:
            from framefox.core.task.worker_manager import WorkerManager

            # Get the worker manager from the service container
            worker_manager = ServiceContainer().get(WorkerManager)
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            async def run_worker():
                """Main worker processing coroutine."""
                worker_manager.running = True
                try:
                    await worker_manager._process_loop()
                except Exception as e:
                    print(f"Worker process error: {e}")

            async def monitor_stop_event():
                """Monitor for shutdown signals and stop the worker gracefully."""
                while not self.worker_stop_event.is_set():
                    await asyncio.sleep(1.0)

                worker_manager.running = False
                loop.stop()

            # Start both coroutines
            loop.create_task(run_worker())
            loop.create_task(monitor_stop_event())

            # Run the event loop until stopped
            loop.run_forever()

        except Exception as e:
            print(f"Worker thread error: {e}")
        finally:
            try:
                loop.close()
            except Exception as e:
                print(f"Error closing loop: {e}")
