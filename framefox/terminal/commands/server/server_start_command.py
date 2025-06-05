import asyncio
import socket
import subprocess
import threading
import time
import webbrowser
from typing import Annotated

import typer

from framefox.core.di.service_container import ServiceContainer
from framefox.terminal.commands.abstract_command import AbstractCommand


class ServerStartCommand(AbstractCommand):
    """
    Command to start the Framefox development server with Uvicorn.

    Supports automatic port detection, background workers, and browser opening.
    """

    # Configuration constants
    BROWSER_DELAY_SECONDS = 2
    MAX_PORT_SEARCH_ATTEMPTS = 10
    WORKER_SHUTDOWN_TIMEOUT = 2.0

    def __init__(self):
        """Initialize the server start command."""
        super().__init__("start")
        self.worker_thread = None
        self.worker_stop_event = None

    def execute(
        self,
        port: Annotated[int, typer.Option("--port", "-p", help="Port to run the server on")] = 8000,
        with_workers: Annotated[bool, typer.Option("--with-workers", help="Start background workers")] = False,
        no_browser: Annotated[bool, typer.Option("--no-browser", help="Don't open browser automatically")] = False,
    ):
        """
        Start the development server with Uvicorn.

        Args:
            port: The port to run the server on (default: 8000)
            with_workers: Whether to start background workers (default: False)
            no_browser: Whether to prevent automatic browser opening (default: False)

        Returns:
            int: Exit code (0 for success, non-zero for failure)
        """
        # Find an available port starting from the requested port
        available_port = self._find_available_port(port)

        # Display startup message
        self.printer.print_msg(
            f"Starting the server on port {available_port}",
            theme="success",
            linebefore=True,
        )

        # Setup background components if requested
        if with_workers:
            self._setup_workers()

        # Handle browser opening based on user preference
        self._handle_browser_opening(available_port, no_browser)

        # Start the Uvicorn server
        return self._start_uvicorn_server(available_port)

    def _find_available_port(self, initial_port: int) -> int:
        """
        Find an available port starting from the initial port.

        Args:
            initial_port: The preferred port to start checking from

        Returns:
            int: An available port number
        """
        current_port = initial_port

        while self._is_port_in_use(current_port) and current_port < initial_port + self.MAX_PORT_SEARCH_ATTEMPTS:
            self.printer.print_msg(f"Port {current_port} already in use, trying {current_port + 1}...", theme="warning")
            current_port += 1

        return current_port

    def _handle_browser_opening(self, port: int, no_browser: bool):
        """
        Handle browser opening based on user preferences.

        Args:
            port: The port where the server will run
            no_browser: Whether to prevent automatic browser opening
        """
        server_url = f"http://localhost:{port}"

        if not no_browser:
            # Start browser opening in a separate daemon thread
            browser_thread = threading.Thread(target=self._open_browser_delayed, args=(server_url,), daemon=True)
            browser_thread.start()
        else:
            # Just inform the user about the URL
            self.printer.print_msg(
                f"Server will be available at {server_url}",
                theme="info",
            )

    def _start_uvicorn_server(self, port: int) -> int:
        """
        Start the Uvicorn server and handle interruptions gracefully.

        Args:
            port: The port to run the server on

        Returns:
            int: Process exit code
        """
        try:
            uvicorn_cmd = ["uvicorn", "main:app", "--reload", "--port", str(port)]
            process = subprocess.run(uvicorn_cmd)
            return process.returncode

        except KeyboardInterrupt:
            self.printer.print_msg("\nStopping the server...", theme="warning")
            self._cleanup_workers()
            return 0

    def _cleanup_workers(self):
        """
        Clean up background worker threads gracefully.

        This method ensures that:
        1. The worker stop event is set to signal shutdown
        2. The worker thread is given time to finish gracefully
        3. Resources are properly released
        """
        if self.worker_stop_event:
            self.worker_stop_event.set()

        if self.worker_thread and self.worker_thread.is_alive():
            # Wait for the worker thread to finish, but don't block indefinitely
            self.worker_thread.join(timeout=self.WORKER_SHUTDOWN_TIMEOUT)

            if self.worker_thread.is_alive():
                self.printer.print_msg("Warning: Worker thread did not shut down gracefully", theme="warning")

    def _is_port_in_use(self, port: int) -> bool:
        """
        Check if a port is already in use.

        Args:
            port: The port number to check

        Returns:
            bool: True if the port is in use, False otherwise
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(("localhost", port)) == 0

    def _open_browser_delayed(self, url: str):
        """
        Open the browser after a delay to allow the server to start.

        Args:
            url: The URL to open in the browser
        """
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

            # Create a new event loop for this thread
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

                # Signal the worker to stop
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
            # Ensure the event loop is properly closed
            try:
                loop.close()
            except Exception as e:
                print(f"Error closing loop: {e}")
