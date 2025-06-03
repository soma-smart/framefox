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

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class ExceptionDataCollector(DataCollector):
    def __init__(self):
        super().__init__("exception", "fa-bug")
        self.exception = None
        self.http_error = None

    def collect_exception(self, exception: Exception, stack_trace: str = None) -> None:
        """Collect a real Python exception"""
        self.exception = {
            "class": exception.__class__.__name__,
            "message": str(exception),
            "code": getattr(exception, "code", 0),
            "trace": stack_trace or traceback.format_exc(),
            "file": self._get_exception_file(exception),
            "line": self._get_exception_line(exception),
        }

    def collect_http_error(self, status_code: int, request: Request) -> None:
        """Collect HTTP error information (4xx, 5xx status codes)"""
        if status_code >= 400:
            error_messages = {
                400: "Bad Request",
                401: "Unauthorized", 
                403: "Forbidden",
                404: "Not Found",
                405: "Method Not Allowed",
                422: "Unprocessable Entity",
                500: "Internal Server Error",
                502: "Bad Gateway",
                503: "Service Unavailable",
                504: "Gateway Timeout"
            }
            
            self.http_error = {
                "type": "HTTP_ERROR",
                "class": f"HTTP{status_code}Error",
                "message": f"{status_code} {error_messages.get(status_code, 'HTTP Error')}",
                "code": status_code,
                "url": str(request.url),
                "method": request.method,
                "path": request.url.path,
                "user_agent": request.headers.get("user-agent", ""),
                "referer": request.headers.get("referer", ""),
                "client_ip": request.client.host if request.client else "unknown",
                # Pas de stack trace pour les erreurs HTTP
                "trace": f"HTTP {status_code} error for {request.method} {request.url.path}",
                "file": "HTTP Response",
                "line": 0,
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
        # Vérifier s'il y a une vraie exception Python
        if hasattr(request.state, "exception"):
            self.exception = request.state.exception

        # Vérifier s'il y a une erreur HTTP (4xx ou 5xx)
        status_code = response.status_code if hasattr(response, "status_code") else 200
        if status_code >= 400:
            self.collect_http_error(status_code, request)

        # Déterminer le type d'erreur à afficher
        has_real_exception = self.exception is not None
        has_http_error = self.http_error is not None
        
        # Priorité aux vraies exceptions Python
        display_exception = self.exception if has_real_exception else self.http_error

        self.data = {
            "exception": display_exception,
            "status_code": status_code,
            "has_exception": has_real_exception or has_http_error,
            "exception_type": (
                "python_exception" if has_real_exception 
                else "http_error" if has_http_error 
                else None
            ),
            "is_http_error": has_http_error and not has_real_exception,
            "is_python_exception": has_real_exception,
        }

    def reset(self):
        """Reset pour la prochaine requête"""
        self.exception = None
        self.http_error = None
        self.data = {}