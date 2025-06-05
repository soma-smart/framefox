import asyncio, socket, subprocess, threading, time, webbrowser, os
from framefox.core.di.service_container import ServiceContainer
from framefox.terminal.commands.abstract_command import AbstractCommand


class ServerStartCommand(AbstractCommand):
    """
    Command to start the development server with optimizations.
    
    This command handles starting a uvicorn server with automatic port detection,
    container pre-warming, optional background workers, and automatic browser opening.
    """
    
    def __init__(self):
        super().__init__("start")
        self.process = None
        self.running = True
        self.worker_thread = None
        self.worker_stop_event = None

    def execute(self, port: int = 8000, *args, **kwargs):
        os.environ['FRAMEFOX_DEV_MODE'] = 'true'
        os.environ['FRAMEFOX_CACHE_ENABLED'] = 'true'
        os.environ['FRAMEFOX_MINIMAL_SCAN'] = 'true'
        
        original_port = port
        
        while self._is_port_in_use(port) and port < original_port + 10:
            self.printer.print_msg(
                f"Port {port} already in use, trying {port+1}...", theme="warning"
            )
            port += 1

        self._prewarm_container()

        with_workers = False
        for arg in args:
            if arg == "--with-workers":
                with_workers = True

        self.printer.print_msg(
            f"Starting optimized dev server on port {port}",
            theme="success",
            linebefore=True,
        )
        
        if with_workers:
            self._setup_workers()
            
        browser_thread = threading.Thread(
            target=self._open_browser, args=(port,), daemon=True
        )
        browser_thread.start()

        try:
            uvicorn_cmd = [
                "uvicorn", "main:app", 
                "--reload", 
                "--reload-delay", "0.5",
                "--reload-dir", "src",
                "--port", str(port)
            ]

            process = subprocess.run(uvicorn_cmd)
            return process.returncode

        except KeyboardInterrupt:
            self.printer.print_msg("\nStopping the server...", theme="warning")
            if self.worker_stop_event:
                self.worker_stop_event.set()
            return 0

    def _prewarm_container(self) -> None:
        try:    
            container = ServiceContainer()
            container.force_complete_scan()
            
            cache_data = container._create_cache_snapshot()
            container._save_service_cache(cache_data)
            
            
        except Exception as e:
            self.printer.print_msg(f"⚠️ Pre-warm failed: {e}", theme="warning")

    def _is_port_in_use(self, port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(("localhost", port)) == 0

    def _open_browser(self, port):
        time.sleep(2)
        url = f"http://localhost:{port}"
        webbrowser.open(url)

    def _setup_workers(self):
        self.printer.print_msg(
            "Starting worker process in background...",
            theme="info",
            linebefore=True,
        )
        try:
            self.worker_stop_event = threading.Event()
            self.worker_thread = threading.Thread(
                target=self._run_worker_thread, daemon=True
            )
            self.worker_thread.start()
        except Exception as e:
            self.printer.print_msg(f"Failed to start worker: {str(e)}", theme="error")

    def _run_worker_thread(self):
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
