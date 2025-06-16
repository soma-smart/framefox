import os
import time
import psutil
from framefox.core.debug.profiler.collector.data_collector import DataCollector

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""

class MemoryDataCollector(DataCollector):
    """
    Memory profiling data collector optimized for ultra-fast performance.
    
    This collector gathers memory usage statistics for the current process,
    including RSS memory usage, memory percentage, and Python-specific memory
    tracking via tracemalloc when available. It also supports template
    rendering memory measurement.
    
    Attributes:
        name (str): Collector identifier set to "memory"
        process (psutil.Process): Process object for memory statistics
        template_render_start (int): Memory baseline for template measurement
        data (dict): Pre-allocated data structure for collected metrics
    """
    name = "memory"

    def __init__(self):
        super().__init__("memory", "fa-memory")
        self.process = psutil.Process(os.getpid())
        self.template_render_start = 0
        
        self.data = {
            "memory_usage_mb": 0.0,
            "memory_percent": 0.0,
            "python_current_mb": 0.0,
            "python_peak_mb": 0.0,
            "template_memory_mb": 0.0,
            "template_render_time_ms": 0.0,
            "status": "unknown",
            "collected_at": 0.0,
        }

    def start_template_measurement(self):
        """Start memory measurement for template rendering."""
        try:
            import tracemalloc
            if tracemalloc.is_tracing():
                self.template_render_start = tracemalloc.get_traced_memory()[0]
            else:
                tracemalloc.start(1)
                self.template_render_start = tracemalloc.get_traced_memory()[0]
        except Exception:
            self.template_render_start = 0

    def end_template_measurement(self) -> float:
        """End memory measurement and return memory used in MB."""
        if self.template_render_start <= 0:
            return 0.0
            
        try:
            import tracemalloc
            if tracemalloc.is_tracing():
                current = tracemalloc.get_traced_memory()[0]
                template_memory = (current - self.template_render_start) / 1024 / 1024
                return max(0.0, template_memory)
        except Exception:
            pass
        return 0.0

    def collect(self, request, response):
        """Collect memory data with ultra-minimal overhead."""
        try:
            memory_info = self.process.memory_info()
            current_mb = memory_info.rss / 1024 / 1024
            
            self.data["memory_usage_mb"] = round(current_mb, 2)
            self.data["memory_percent"] = round(self.process.memory_percent(), 1)
            self.data["status"] = "high" if current_mb > 500 else "normal"
            self.data["collected_at"] = time.time()
            
            try:
                import tracemalloc
                if tracemalloc.is_tracing():
                    current, peak = tracemalloc.get_traced_memory()
                    self.data["python_current_mb"] = round(current / 1024 / 1024, 2)
                    self.data["python_peak_mb"] = round(peak / 1024 / 1024, 2)
                else:
                    self.data["python_current_mb"] = 0.0
                    self.data["python_peak_mb"] = 0.0
            except Exception:
                self.data["python_current_mb"] = 0.0
                self.data["python_peak_mb"] = 0.0

        except Exception:
            self.data.update({
                "memory_usage_mb": 0.0,
                "memory_percent": 0.0,
                "python_current_mb": 0.0,
                "python_peak_mb": 0.0,
                "status": "error",
                "collected_at": time.time(),
            })

    def add_template_metrics(self, template_memory_mb: float, render_time_ms: float):
        """Add template rendering metrics."""
        self.data["template_memory_mb"] = round(template_memory_mb, 2)
        self.data["template_render_time_ms"] = round(render_time_ms, 2)

    def reset(self):
        """Reset for next request."""
        self.template_render_start = 0
        self.data.update({
            "template_memory_mb": 0.0,
            "template_render_time_ms": 0.0,
            "status": "unknown",
        })