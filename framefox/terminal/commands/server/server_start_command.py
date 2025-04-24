import signal
import subprocess
import sys
import threading
import asyncio
import os

from framefox.core.di.service_container import ServiceContainer
from framefox.terminal.commands.abstract_command import AbstractCommand
from framefox.terminal.commands.server.worker_command import WorkerCommand


class ServerStartCommand(AbstractCommand):
    def __init__(self):
        super().__init__("server:start")
        self.process = None
        self.running = True
        self.worker_thread = None
        self.worker_stop_event = None

    def execute(self, port: int = 8000, *args, **kwargs):
        """
        Démarre le serveur de développement avec Uvicorn
        Start the uvicorn server.
        """
        with_workers = False

        # Traiter les arguments supplémentaires
        for arg in args:
            if arg == "--with-workers":
                with_workers = True

        self.printer.print_msg(
            f"Starting the server on port {port}",
            theme="success",
            linebefore=True,
        )

        if with_workers:
            self._setup_workers()

        # Utiliser directement subprocess.run() pour une sortie immédiate
        # et capturer correctement les erreurs à l'écran
        try:
            uvicorn_cmd = ["uvicorn", "main:app",
                           "--reload", "--port", str(port)]

            # Démarrer le serveur sans redirection de sortie
            # pour assurer que tous les messages s'affichent correctement
            process = subprocess.run(uvicorn_cmd)

            return process.returncode
        except KeyboardInterrupt:
            self.printer.print_msg("\nStopping the server...", theme="warning")
            if self.worker_stop_event:
                self.worker_stop_event.set()
            return 0

    def _setup_workers(self):
        """Configure le thread worker en arrière-plan si demandé"""
        self.printer.print_msg(
            "Starting worker process in background...",
            theme="info",
            linebefore=True,
        )

        try:
            self.worker_stop_event = threading.Event()
            self.worker_thread = threading.Thread(
                target=self._run_worker_thread,
                daemon=True
            )
            self.worker_thread.start()
        except Exception as e:
            self.printer.print_msg(
                f"Failed to start worker: {str(e)}",
                theme="error"
            )

    def _run_worker_thread(self):
        """Exécute les workers dans un thread séparé"""
        try:
            from framefox.core.task.worker_manager import WorkerManager
            worker_manager = ServiceContainer().get(WorkerManager)

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            async def run_worker():
                worker_manager.running = True
                try:
                    await worker_manager._process_loop()
                except Exception as e:
                    print(f"Worker process error: {e}")

            async def monitor_stop_event():
                while not self.worker_stop_event.is_set():
                    await asyncio.sleep(1.0)
                worker_manager.running = False
                loop.stop()

            loop.create_task(run_worker())
            loop.create_task(monitor_stop_event())
            loop.run_forever()
        except Exception as e:
            print(f"Worker thread error: {e}")
