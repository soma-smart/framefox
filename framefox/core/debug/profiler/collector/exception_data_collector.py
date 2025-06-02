import datetime
import json
import logging
import os
import random
import shutil
import time
import traceback
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

import psutil
from fastapi import Request, Response

from framefox.core.config.settings import Settings
from framefox.core.debug.profiler.collector.data_collector import DataCollector


class ExceptionDataCollector(DataCollector):
    def __init__(self):
        super().__init__("exception", "fa-bug")
        self.exception = None

    def collect_exception(self, exception: Exception, stack_trace: str = None) -> None:
        self.exception = {
            "class": exception.__class__.__name__,
            "message": str(exception),
            "code": getattr(exception, "code", 0),
            "trace": stack_trace or traceback.format_exc(),
            "file": self._get_exception_file(exception),
            "line": self._get_exception_line(exception),
        }

    def _get_exception_file(self, exception):
        if hasattr(exception, "__traceback__") and exception.__traceback__:
            return exception.__traceback__.tb_frame.f_code.co_filename
        return "Unknown"

    def _get_exception_line(self, exception):
        if hasattr(exception, "__traceback__") and exception.__traceback__:
            return exception.__traceback__.tb_lineno
        return 0

    def collect(self, request: Request, response: Response) -> None:
        if hasattr(request.state, "exception"):
            self.exception = request.state.exception

        self.data = {
            "exception": self.exception,
            "status_code": (
                response.status_code if hasattr(response, "status_code") else 500
            ),
            "has_exception": self.exception is not None,
        }
