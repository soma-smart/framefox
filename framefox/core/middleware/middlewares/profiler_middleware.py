import logging
import sys
import time
import traceback
from typing import Callable

from fastapi import Request, Response
from fastapi.responses import StreamingResponse
from starlette.middleware.base import BaseHTTPMiddleware

from framefox.core.config.settings import Settings
from framefox.core.debug.profiler.profiler import Profiler
from framefox.core.di.service_container import ServiceContainer
from framefox.core.request.static_resource_detector import StaticResourceDetector
from framefox.core.templates.template_renderer import TemplateRenderer

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class ProfilerMiddleware(BaseHTTPMiddleware):
    """
    Middleware for profiling HTTP requests in a FastAPI application.

    This middleware collects comprehensive request data including:
    - Request and response details
    - SQL queries and database operations
    - Memory usage statistics
    - Exception information
    - Performance metrics

    For HTML responses, it automatically injects a profiler toolbar
    for debugging and performance monitoring when profiling is enabled.

    Args:
        app: The FastAPI application instance
    """

    def __init__(self, app):
        super().__init__(app)
        self.profiler = Profiler()
        self.settings = Settings()
        if self.settings.profiler_enabled:
            self.profiler.enable()
        self.logger = logging.getLogger("PROFILER")
        self.logger.setLevel(logging.DEBUG)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        path = request.url.path
        if StaticResourceDetector.is_static_resource(path):
            return await call_next(request)

        start_time = time.time()
        request.state.request_start_time = start_time

        token = None
        profiler_enabled = False

        request_collector = self.profiler.get_collector("request")
        if request_collector and request.method in ("POST", "PUT", "PATCH"):
            try:
                await request_collector.capture_request_body(request)
            except Exception as e:
                self.logger.debug(f"Could not capture request body: {e}")

        sql_collector = self.profiler.get_collector("database")
        if sql_collector:
            sql_collector.start_request()

        response = await call_next(request)

        try:
            profiler_enabled = self.profiler.is_enabled()

            if profiler_enabled:
                try:
                    token = self.profiler.collect(request, response)
                    if token:
                        request.state.profiler_token = token
                except Exception as e:
                    self.logger.debug(f"Failed to collect profiler data: {e}")
                    token = None

            content_type = response.headers.get("content-type", "")
            is_html = "text/html" in content_type

            if not is_html or not profiler_enabled or not token:
                return response

            if response.status_code in (301, 302, 303, 307, 308):
                return response

            is_streaming = (
                isinstance(response, StreamingResponse)
                or type(response).__name__.endswith("StreamingResponse")
                or hasattr(response, "body_iterator")
            )

            if is_streaming:
                return await self._handle_streaming_response(response, token, start_time, request)

            if hasattr(response, "body"):
                response_text = response.body.decode("utf-8")

                has_body_tag = "</body>" in response_text

                if has_body_tag:
                    try:
                        html = self._generate_profiler_bar(token, time.time() - start_time, request)

                        response_text = response_text.replace("</body>", f"{html}</body>")
                        response.body = response_text.encode("utf-8")
                        response.headers["content-length"] = str(len(response.body))
                    except Exception as e:
                        self.logger.debug(f"Failed to inject profiler bar: {e}")

            return response

        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback_details = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            self.logger.error(f"Unhandled exception in profiler: {str(e)}\n{traceback_details}")
            return response

    async def _handle_streaming_response(
        self,
        response: StreamingResponse,
        token: str,
        start_time: float,
        request: Request,
    ) -> StreamingResponse:
        try:
            profiler_html = self._generate_profiler_bar(token, time.time() - start_time, request)

            content_chunks = []

            async def wrapped_stream():
                try:
                    async for chunk in response.body_iterator:
                        content_chunks.append(chunk)

                    full_content = b"".join(content_chunks)

                    try:
                        content_str = full_content.decode("utf-8")

                        if "</body>" in content_str:
                            modified_content = content_str.replace("</body>", f"{profiler_html}</body>")
                            yield modified_content.encode("utf-8")
                        else:
                            yield full_content
                    except UnicodeDecodeError as e:
                        self.logger.error(f"Could not decode content: {e}")
                        yield full_content

                except Exception as e:
                    self.logger.error(f"Error during stream capture: {e}")
                    for chunk in content_chunks:
                        yield chunk

            headers = dict(response.headers)

            if "content-length" in headers:
                del headers["content-length"]

            new_response = StreamingResponse(
                content=wrapped_stream(),
                status_code=response.status_code,
                headers=headers,
                media_type=response.media_type,
            )

            return new_response

        except Exception as e:
            self.logger.error(f"Fatal exception in _handle_streaming_response: {str(e)}\n{traceback.format_exc()}")
            return response

    def _generate_profiler_bar(self, token: str, duration: float, request: Request) -> str:
        profile = self.profiler.get_profile(token)

        duration_ms = round(duration * 1000, 2)

        memory_data = profile.get("memory", {})
        memory = 0

        if memory_data:
            memory = memory_data.get("memory_usage_mb") or memory_data.get("memory_usage") or 0

        route = request.url.path
        status_code = profile.get("request", {}).get("status_code", 200) if "request" in profile else 200

        context = {
            "token": token,
            "profile": profile,
            "duration": duration_ms,
            "memory": memory,
            "route": route,
            "status_code": status_code,
        }

        try:
            container = ServiceContainer()
            template_renderer = container.get(TemplateRenderer)

            if template_renderer:
                return template_renderer.render("profiler/toolbar.html", context)
        except Exception as e:
            self.logger.error(f"Error rendering profiler template: {str(e)}")

        return ""
