import time

from fastapi import Request, Response

from framefox.core.debug.profiler.collector.data_collector import DataCollector


class TimeDataCollector(DataCollector):
    def __init__(self):
        super().__init__("time", "fa-clock")

    def collect(self, request: Request, response: Response) -> None:
        end_time = time.time()
        start_time = getattr(request.state, "request_start_time", None)

        if start_time is None:
            request_duration = getattr(request.state, "request_duration", None)
            if request_duration:
                start_time = end_time - (request_duration / 1000)
            else:
                start_time = end_time - 0.01

        self.data = {
            "start_time": start_time,
            "end_time": end_time,
            "duration": round((end_time - start_time) * 1000, 2),
        }
