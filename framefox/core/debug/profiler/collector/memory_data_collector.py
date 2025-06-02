import os

import psutil
from fastapi import Request, Response

from framefox.core.debug.profiler.collector.data_collector import DataCollector


class MemoryDataCollector(DataCollector):
    def __init__(self):
        super().__init__("memory", "fa-memory")

    def collect(self, request: Request, response: Response) -> None:
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        self.data = {
            "memory_usage": memory_info.rss / (1024 * 1024),
            "peak_memory": memory_info.vms / (1024 * 1024),
        }
