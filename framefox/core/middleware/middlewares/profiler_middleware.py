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

        try:
            response = await call_next(request)
        except Exception as e:

            exception_collector = self.profiler.get_collector("exception")
            if exception_collector:
                stack_trace = traceback.format_exc()
                exception_collector.collect_exception(e, stack_trace)

            request.state.exception = {
                "class": e.__class__.__name__,
                "message": str(e),
                "trace": traceback.format_exc(),
            }

            raise e

        try:
            content_type = response.headers.get("content-type", "")
            is_html = "text/html" in content_type

            if not is_html or not self.profiler.is_enabled():
                return response

            if response.status_code in (301, 302, 303, 307, 308):
                return response

            token = self.profiler.collect(request, response)

            if not token:
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
                    html = self._generate_profiler_bar(token, time.time() - start_time, request)

                    response_text = response_text.replace("</body>", f"{html}</body>")
                    response.body = response_text.encode("utf-8")
                    response.headers["content-length"] = str(len(response.body))

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
        memory = profile.get("memory", {}).get("memory_usage", 0) if "memory" in profile else 0
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
