import logging
import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from framefox.core.events.decorator.dispatch_event import DispatchEvent
from framefox.core.logging.context_logger import ContextLogger
from framefox.core.request.request_stack import RequestStack
from framefox.core.request.static_resource_detector import StaticResourceDetector

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class RequestMiddleware(BaseHTTPMiddleware):
    """
    RequestMiddleware is a custom middleware for the Framefox framework.
    It manages the request lifecycle by:
    1. Setting the current request in the RequestStack.
    2. Creating a unique request ID and logging context.
    3. Logging request metrics and performance.
    4. Dispatching events related to the request lifecycle.
    """

    def __init__(self, app):
        super().__init__(app)
        self.logger = ContextLogger.get_logger("REQUEST")

    @DispatchEvent(
        event_before="kernel.request_received", event_after="kernel.finish_request"
    )
    async def dispatch(self, request: Request, call_next):
        RequestStack.set_request(request)
        request_id = ContextLogger.set_request_id()
        ContextLogger.set_context_value(
            "client_ip", request.client.host if request.client else "unknown"
        )
        ContextLogger.set_context_value("method", request.method)
        ContextLogger.set_context_value("path", request.url.path)
        path = request.url.path
        is_static_resource = StaticResourceDetector.is_static_resource(path)
        if not is_static_resource:
            self.logger.info(f"Incoming request: {request.method} {path}")
        start_time = time.time()
        try:
            response = await call_next(request)
            duration_ms = round((time.time() - start_time) * 1000, 2)
            ContextLogger.set_context_value("status_code", response.status_code)
            ContextLogger.set_context_value("duration_ms", duration_ms)
            return response
        except Exception as e:
            duration_ms = round((time.time() - start_time) * 1000, 2)
            ContextLogger.set_context_value("duration_ms", duration_ms)
            ContextLogger.set_context_value("error", str(e))
            self.logger.error(
                f"Request failed: {request.method} {path} - Error: {str(e)} - Duration: {duration_ms} ms"
            )
            raise
