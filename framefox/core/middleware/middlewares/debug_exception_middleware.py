from fastapi import Request
from fastapi.responses import HTMLResponse, JSONResponse
import traceback
import logging
from framefox.core.di.service_container import ServiceContainer
from framefox.core.templates.template_renderer import TemplateRenderer

class DebugExceptionMiddleware:
    """Middleware to capture all exceptions and display them with Framefox style."""
    
    def __init__(self, app, settings):
        self.app = app
        self.container = ServiceContainer()
        self.settings = settings
        self.logger = logging.getLogger("Application")

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        request = Request(scope)
        
        try:
            await self.app(scope, receive, send)
        except Exception as exc:
            self._log_exception(request, exc)
            
            response = await self._handle_exception(request, exc)
            await response(scope, receive, send)

    def _log_exception(self, request: Request, exc: Exception):
        """Log the exception with complete stack trace for developers."""
        try:
            method = request.method
            path = request.url.path
            
            stack_trace = traceback.format_exc()
            
            self.logger.error(
                f"{method} {path} - {exc.__class__.__name__}: {str(exc)}\n"
                f"Stack Trace:\n{stack_trace}"
            )
            
            exception_type = exc.__class__.__name__
            exception_message = str(exc)
            
       
            self.logger.error(f"{exception_type}: {exception_message}")
                
        except Exception as log_error:
            self.logger.error(f"Failed to log exception details: {log_error}")
            self.logger.error(f"Original exception: {exc}")

    async def _handle_exception(self, request: Request, exc: Exception) -> HTMLResponse:
        """Handle the exception with Framefox debug view."""
        
        accept_header = request.headers.get("accept", "")
        
        if "application/json" in accept_header or "text/html" not in accept_header:
            return JSONResponse(
                content={
                    "error": "Internal Server Error", 
                    "status_code": 500,
                    "message": str(exc) if self.settings.is_debug else "An error occurred"
                }, 
                status_code=500
            )
        
        if self.settings.is_debug:
            container = ServiceContainer()
            template_renderer = container.get(TemplateRenderer)
            
            profiler_token = getattr(request.state, 'profiler_token', None)
            
            traceback_str = self._format_traceback(exc)
            source_info = self._parse_traceback_for_source_info(traceback_str)
            
            error_context = {
                "request": request,
                "error": "Internal Server Error",
                "exception": exc,
                "exception_type": type(exc).__name__,
                "exception_message": str(exc),
                "traceback": traceback_str,
                "profiler_token": profiler_token,
                "source_info": source_info
            }
            
            html_content = template_renderer.render("debug_error.html", error_context)
            return HTMLResponse(content=html_content, status_code=500)
        else:
            container = ServiceContainer()
            template_renderer = container.get(TemplateRenderer)
            html_content = template_renderer.render("500.html", {"request": request})
            return HTMLResponse(content=html_content, status_code=500)

    def _format_traceback(self, exc: Exception) -> str:
        """Format traceback for debug display."""
        return traceback.format_exc()

    def _parse_traceback_for_source_info(self, traceback_str: str) -> dict:
        """Parse traceback to extract real error information."""
        lines = traceback_str.split('\n')
        
        for line in lines:
            if 'File "' in line and 'line ' in line:
                if any(x in line for x in ['/middleware/', '/starlette/', '/fastapi/', '/uvicorn/']):
                    continue
                    
                if 'src/' in line or not any(x in line for x in ['/site-packages/', '/lib/python']):
                    try:
                        file_start = line.find('File "') + 6
                        file_end = line.find('"', file_start)
                        file_path = line[file_start:file_end]
                        
                        line_start = line.find('line ') + 5
                        line_end = line.find(',', line_start)
                        line_number = line[line_start:line_end]
                        
                        if 'in ' in line:
                            func_start = line.rfind('in ') + 3
                            function_name = line[func_start:].strip()
                        else:
                            function_name = "Unknown"
                        
                        return {
                            'file': file_path.split('/')[-1],
                            'full_file': file_path,
                            'line': line_number,
                            'function': function_name
                        }
                    except Exception:
                        continue
        
        return {
            'file': 'Unknown',
            'full_file': 'Unknown', 
            'line': 'Unknown',
            'function': 'Unknown'
        }
