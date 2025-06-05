import gc, psutil, tracemalloc, time
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
    Memory profiling data collector that tracks system memory usage, Python memory allocation,
    and template rendering memory consumption.
    
    This collector provides real-time memory metrics including RSS memory usage,
    Python heap memory tracking via tracemalloc, garbage collection statistics,
    and template-specific memory measurements.
    """
    name = "memory"

    def __init__(self):
        super().__init__("memory", "fa-memory")
        self.process = psutil.Process()
        self.start_memory = 0
        self.template_render_start = 0
        
        self._initialize_data()
        
        if not tracemalloc.is_tracing():
            tracemalloc.start(1)

    def _initialize_data(self):
        self.data = {
            "memory_usage_mb": 0.0,
            "memory_percent": 0.0,
            "python_current_mb": 0.0,
            "python_peak_mb": 0.0,
            "gc_objects_count": 0,
            
            "template_memory_mb": 0.0,
            "template_render_time_ms": 0.0,
            
            "status": "unknown",
            "collected_at": time.time(),
            
            "gc_generation_0": 0,
            "gc_generation_1": 0, 
            "gc_generation_2": 0,
        }

    def start_template_measurement(self):
        self.template_render_start = tracemalloc.get_traced_memory()[0]
        gc.collect()

    def end_template_measurement(self) -> float:
        if self.template_render_start > 0:
            current = tracemalloc.get_traced_memory()[0]
            template_memory = (current - self.template_render_start) / 1024 / 1024
            return max(0, template_memory)
        return 0

    def collect(self, request, response):
        try:
            memory_info = self.process.memory_info()
            memory_percent = self.process.memory_percent()
            
            current, peak = tracemalloc.get_traced_memory()

            current_mb = memory_info.rss / 1024 / 1024
            python_current_mb = current / 1024 / 1024
            python_peak_mb = peak / 1024 / 1024

            gc_objects = len(gc.get_objects())

            self.data.update({
                "memory_usage_mb": round(current_mb, 2),
                "memory_percent": round(memory_percent, 1),
                "python_current_mb": round(python_current_mb, 2),
                "python_peak_mb": round(python_peak_mb, 2),
                "gc_objects_count": gc_objects,
                
                "status": "normal" if current_mb < 500 else "high",
                "collected_at": time.time(),
                
                "gc_generation_0": gc.get_count()[0],
                "gc_generation_1": gc.get_count()[1], 
                "gc_generation_2": gc.get_count()[2],
            })

        except Exception as e:
            self.data.update({
                "error": str(e),
                "memory_usage_mb": 0,
                "memory_percent": 0,
                "python_current_mb": 0,
                "python_peak_mb": 0,
                "gc_objects_count": 0,
                "status": "error"
            })

    def add_template_metrics(self, template_memory_mb: float, render_time_ms: float):
        self.data["template_memory_mb"] = round(template_memory_mb, 2)
        self.data["template_render_time_ms"] = round(render_time_ms, 2)

    def reset(self):
        self._initialize_data()
        self.template_render_start = 0
