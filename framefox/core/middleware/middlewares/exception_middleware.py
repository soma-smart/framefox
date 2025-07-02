import logging
import re
import traceback

from fastapi import Request
from fastapi.responses import HTMLResponse, JSONResponse

from framefox.core.config.settings import Settings
from framefox.core.debug.exception.auth_exception import (
    AuthenticationError,
    AuthException,
    AuthorizationError,
    InvalidTokenError,
    TokenExpiredError,
)
from framefox.core.debug.exception.base_exception import (
    ConfigurationException,
    FramefoxException,
)
from framefox.core.debug.exception.database_exception import (
    DatabaseConnectionError,
    DatabaseException,
    DatabaseIntegrityError,
    TableNotFoundError,
    UnsupportedDatabaseDriverError,
)
from framefox.core.debug.exception.file_exception import (
    FileException,
    FileNotFoundError,
    FilePermissionError,
    FileSizeError,
    FileUploadError,
)
from framefox.core.debug.exception.http_exception import (
    BadRequestError,
    ConflictError,
    ForbiddenError,
    HttpException,
    MethodNotAllowedError,
    NotFoundError,
    TooManyRequestsError,
    UnauthorizedError,
    UnprocessableEntityError,
)
from framefox.core.debug.exception.service_exception import (
    ExternalServiceError,
    RateLimitExceededError,
    ServiceException,
    TimeoutError,
)
from framefox.core.debug.exception.settings_exception import (
    ConfigurationFileNotFoundError,
    EnvironmentVariableNotFoundError,
    InvalidConfigurationError,
    SettingsException,
)
from framefox.core.debug.exception.template_exception import (
    TemplateException,
    TemplateNotFoundError,
    TemplateRenderError,
    TemplateSyntaxError,
)
from framefox.core.debug.exception.validation_exception import (
    MultipleValidationErrors,
    ValidationError,
    ValidationException,
)
from framefox.core.debug.sentry.sentry_manager import SentryManager
from framefox.core.di.service_container import ServiceContainer
from framefox.core.templates.template_renderer import TemplateRenderer


class ExceptionMiddleware:
    """Enhanced middleware for comprehensive exception handling"""

    def __init__(self, app):
        self.app = app
        self.container = ServiceContainer()
        self.settings = Settings()
        self.logger = logging.getLogger("Application")
        self.template_renderer = self.container.get(TemplateRenderer)
        self.sentry_manager = SentryManager()

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        request = Request(scope)

        try:
            await self.app(scope, receive, send)
        except Exception as exc:
            transformed_exc = self._transform_exception(exc)
            request.state.exception = transformed_exc

            # Send to Sentry if enabled
            if self.sentry_manager.is_enabled():
                try:
                    # Add request context
                    self.sentry_manager.set_context(
                        "request",
                        {
                            "url": str(request.url),
                            "method": request.method,
                            "headers": dict(request.headers),
                            "path": request.url.path,
                        },
                    )

                    # Add framework context
                    self.sentry_manager.set_tag("framework", "framefox")
                    self.sentry_manager.set_tag("exception_type", type(transformed_exc).__name__)

                    # Capture the exception
                    self.sentry_manager.capture_exception(transformed_exc)
                except Exception as sentry_error:
                    self.logger.error(f"Failed to send exception to Sentry: {sentry_error}")

            try:
                from framefox.core.debug.profiler.profiler import Profiler

                profiler = Profiler()
                if profiler.is_enabled():
                    error_token = profiler.collect_error_profile(request, transformed_exc)
                    if error_token:
                        request.state.profiler_token = error_token
            except Exception:
                pass

            self._log_exception_clean(request, transformed_exc, exc)

            response = await self._handle_exception(request, transformed_exc)
            await response(scope, receive, send)

    def _transform_exception(self, exc: Exception) -> Exception:
        """Transform technical exceptions into user-friendly Framefox exceptions"""
        exc_str = str(exc)
        exc_type = str(type(exc))

        if isinstance(exc, FramefoxException):
            return exc

        if "no such table:" in exc_str:
            table_match = re.search(r"no such table: (\w+)", exc_str)
            table_name = table_match.group(1) if table_match else "unknown"
            return TableNotFoundError(table_name, exc)

        if "PendingRollbackError" in exc_str and "no such table:" in exc_str:
            table_match = re.search(r"no such table: (\w+)", exc_str)
            table_name = table_match.group(1) if table_match else "unknown"
            return TableNotFoundError(table_name, exc)

        if "IntegrityError" in exc_type:
            constraint_match = re.search(r"UNIQUE constraint failed: (\w+)", exc_str)
            constraint = constraint_match.group(1) if constraint_match else None
            return DatabaseIntegrityError(constraint, exc)

        if "sqlalchemy.exc." in exc_type:
            return DatabaseException("Database operation failed", exc)

        # Handle unsupported database driver errors
        if "unsupported database driver" in exc_str.lower() or "can't load plugin" in exc_str.lower():
            driver_match = re.search(r"sqlalchemy\.dialects:(\w+)", exc_str)
            driver_name = driver_match.group(1) if driver_match else "unknown"
            return UnsupportedDatabaseDriverError(driver_name, exc)

        if hasattr(exc, "status_code"):
            status_code = getattr(exc, "status_code")
            if status_code == 400:
                return BadRequestError(str(exc), exc)
            elif status_code == 401:
                return UnauthorizedError(str(exc), exc)
            elif status_code == 403:
                return ForbiddenError(str(exc), exc)
            elif status_code == 404:
                return NotFoundError(str(exc), exc)
            elif status_code == 405:
                return MethodNotAllowedError("Unknown", [], exc)
            elif status_code == 409:
                return ConflictError(str(exc), exc)
            elif status_code == 422:
                return UnprocessableEntityError(str(exc), exc)
            elif status_code == 429:
                return TooManyRequestsError(None, exc)

        if "FileNotFoundError" in exc_type or "No such file or directory" in exc_str:
            file_match = re.search(r"'([^']+)'", exc_str)
            file_path = file_match.group(1) if file_match else "unknown"
            return FileNotFoundError(file_path, exc)

        if "jinja2.exceptions.TemplateNotFound" in exc_type or exc_type.endswith("TemplateNotFound"):
            template_match = re.search(r"template '([^']+)'", exc_str)
            if not template_match:
                template_match = re.search(r"([^/\s]+\.html)", exc_str)
            template_name = template_match.group(1) if template_match else "unknown"
            return TemplateNotFoundError(template_name, exc)

        if "jinja2.exceptions.TemplateSyntaxError" in exc_type or exc_type.endswith("TemplateSyntaxError"):
            template_match = re.search(r"template '([^']+)'", exc_str)
            if not template_match:
                template_match = re.search(r"([^/\s]+\.html)", exc_str)
            template_name = template_match.group(1) if template_match else "unknown"

            line_match = re.search(r"line (\d+)", exc_str)
            line_number = int(line_match.group(1)) if line_match else None

            return TemplateSyntaxError(template_name, line_number, exc)

        if "jinja2.exceptions.UndefinedError" in exc_type or exc_type.endswith("UndefinedError"):
            template_match = re.search(r"template '([^']+)'", exc_str)
            if not template_match:
                template_match = re.search(r"([^/\s]+\.html)", exc_str)
            template_name = template_match.group(1) if template_match else "unknown"

            return TemplateRenderError(template_name, f"Undefined variable: {exc_str}", exc)

        if "HTTPException" in exc_type and any(keyword in exc_str.lower() for keyword in ["template", ".html"]):
            template_match = re.search(r"([^/\s]+\.html)", exc_str)
            template_name = template_match.group(1) if template_match else "unknown"

            if "not found" in exc_str.lower() or "does not exist" in exc_str.lower():
                return TemplateNotFoundError(template_name, exc)
            else:
                return TemplateRenderError(template_name, str(exc), exc)

        if "TemplateNotFound" in exc_type or "jinja2.exceptions.TemplateNotFound" in exc_type:
            template_match = re.search(r"template '([^']+)'", exc_str)
            if not template_match:
                template_match = re.search(r"([^/\s]+\.html)", exc_str)
            template_name = template_match.group(1) if template_match else "unknown"
            return TemplateNotFoundError(template_name, exc)

        if "TemplateSyntaxError" in exc_type or "jinja2.exceptions.TemplateSyntaxError" in exc_type:
            template_match = re.search(r"template '([^']+)'", exc_str)
            if not template_match:
                template_match = re.search(r"([^/\s]+\.html)", exc_str)
            template_name = template_match.group(1) if template_match else "unknown"

            line_match = re.search(r"line (\d+)", exc_str)
            line_number = int(line_match.group(1)) if line_match else None

            return TemplateSyntaxError(template_name, line_number, exc)

        if "UndefinedError" in exc_type or "jinja2.exceptions.UndefinedError" in exc_type:
            template_match = re.search(r"template '([^']+)'", exc_str)
            if not template_match:
                template_match = re.search(r"([^/\s]+\.html)", exc_str)
            template_name = template_match.group(1) if template_match else "unknown"

            return TemplateRenderError(template_name, f"Undefined variable: {exc_str}", exc)

        if "HTTPException" in exc_type and "template" in exc_str.lower():
            template_match = re.search(r"([^/\s]+\.html)", exc_str)
            template_name = template_match.group(1) if template_match else "unknown"

            if "not found" in exc_str.lower() or "does not exist" in exc_str.lower():
                return TemplateNotFoundError(template_name, exc)
            else:
                return TemplateRenderError(template_name, str(exc), exc)

        if "PermissionError" in exc_type or "Permission denied" in exc_str:
            file_match = re.search(r"'([^']+)'", exc_str)
            file_path = file_match.group(1) if file_match else "unknown"
            return FilePermissionError(file_path, "access", exc)

        if "TimeoutError" in exc_type or "timeout" in exc_str.lower():
            return TimeoutError("request", None, exc)

        if "ConnectionError" in exc_type or "connection" in exc_str.lower():
            if "database" in exc_str.lower():
                return DatabaseConnectionError("Database connection failed", exc)
            else:
                return ExternalServiceError("external service", "connection", exc)

        if "authentication" in exc_str.lower() or "login" in exc_str.lower():
            return AuthenticationError(str(exc), exc)

        if "authorization" in exc_str.lower() or "permission" in exc_str.lower():
            return AuthorizationError(None, None, exc)

        if "token" in exc_str.lower() and ("expired" in exc_str.lower() or "invalid" in exc_str.lower()):
            if "expired" in exc_str.lower():
                return TokenExpiredError("token", exc)
            else:
                return InvalidTokenError("token", exc)

        return FramefoxException(f"Unhandled error: {str(exc)}", exc, "UNHANDLED_ERROR")

    def _log_exception_clean(self, request: Request, user_exc: Exception, original_exc: Exception):
        """Log exceptions cleanly without sensitive data"""
        try:
            if isinstance(user_exc, FramefoxException):
                exception_name = type(user_exc).__name__
                log_message = f"{user_exc.message}"
                exception_logger = logging.getLogger(exception_name)
                exception_logger.error(log_message)
            else:
                exception_name = type(user_exc).__name__
                log_message = f"{str(user_exc)}"
                exception_logger = logging.getLogger(exception_name)
                exception_logger.error(log_message)
        except Exception as log_error:
            self.logger.error(f"Failed to log exception: {log_error}")

    def _sanitize_sql_parameters(self, text: str) -> str:
        """Remove sensitive data from SQL parameters"""
        if not text:
            return text

        text = re.sub(r"\$2[aby]\$\d+\$[A-Za-z0-9./]{53}", "[HASHED_PASSWORD]", text)
        text = re.sub(
            r"\$argon2[id]\$[^,]*,[^,]*,[^,]*\$[A-Za-z0-9+/=]*",
            "[HASHED_PASSWORD]",
            text,
        )
        text = re.sub(r"\$scrypt\$[^$]*\$[^$]*\$[A-Za-z0-9+/=]*", "[HASHED_PASSWORD]", text)
        text = re.sub(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "[EMAIL]", text)
        text = re.sub(r"\[parameters: \([^)]*\)\]", "[parameters: [SANITIZED]]", text)
        text = re.sub(
            r'(api[_-]?key|token|secret)["\s]*[:=]["\s]*[A-Za-z0-9+/=]{10,}',
            r"\1: [REDACTED]",
            text,
            flags=re.IGNORECASE,
        )

        return text

    def _get_clean_traceback(self, exc: Exception) -> str:
        """Get a clean traceback focusing on user code"""
        full_traceback = traceback.format_exc()
        lines = full_traceback.split("\n")

        filtered_lines = []
        skip_patterns = [
            "/site-packages/",
            "/lib/python",
            "/starlette/",
            "/fastapi/",
            "/uvicorn/",
            "/middleware/base.py",
            "/routing.py",
        ]

        for line in lines:
            if line.strip().startswith(("Traceback", "sqlalchemy.exc.", "sqlite3.")):
                filtered_lines.append(line)
            elif 'File "' in line:
                if not any(pattern in line for pattern in skip_patterns):
                    filtered_lines.append(line)
            elif line.strip() and not any(pattern in line for pattern in skip_patterns):
                if filtered_lines and 'File "' in filtered_lines[-1]:
                    filtered_lines.append(line)

        return "\n".join(filtered_lines) if filtered_lines else full_traceback

    async def _handle_exception(self, request: Request, exc: Exception) -> HTMLResponse:
        """Handle exception with clean user interface"""
        accept_header = request.headers.get("accept", "")

        if "application/json" in accept_header or "text/html" not in accept_header:
            return self._create_json_response(exc)

        if self.settings.is_debug:
            return await self._render_debug_page(request, exc)
        else:
            return await self._render_production_error_page(request, exc)

    def _create_json_response(self, exc: Exception) -> JSONResponse:
        """Create JSON response based on exception type"""
        status_code = getattr(exc, "status_code", 500)
        error_code = getattr(exc, "error_code", "INTERNAL_ERROR")

        response_data = {
            "error": type(exc).__name__,
            "error_code": error_code,
            "message": exc.message if hasattr(exc, "message") else str(exc),
            "status_code": status_code,
        }

        if isinstance(exc, TableNotFoundError):
            response_data.update(
                {
                    "suggestion": "Run 'framefox database create' to set up the database",
                    "table_name": exc.table_name,
                }
            )
        elif isinstance(exc, ValidationError):
            response_data.update({"field": exc.field, "validation_message": exc.validation_message})
        elif isinstance(exc, MultipleValidationErrors):
            response_data.update({"errors": exc.errors})
        elif isinstance(exc, AuthorizationError):
            response_data.update({"resource": exc.resource, "action": exc.action})
        elif isinstance(exc, FileUploadError):
            response_data.update({"filename": exc.filename, "reason": exc.reason})
        elif isinstance(exc, TimeoutError):
            response_data.update({"operation": exc.operation, "timeout_seconds": exc.timeout_seconds})

        return JSONResponse(content=response_data, status_code=status_code)

    async def _render_debug_page(self, request: Request, exc: Exception) -> HTMLResponse:
        """Render debug page with comprehensive exception information"""
        profiler_token = getattr(request.state, "profiler_token", None)
        error_code = getattr(exc, "error_code", "UNKNOWN")
        exception_category = self._get_exception_category(exc)
        specific_context = self._get_exception_specific_context(exc)

        error_context = {
            "request": request,
            "exception_type": type(exc).__name__,
            "exception_message": exc.message if hasattr(exc, "message") else str(exc),
            "error_code": error_code,
            "exception_category": exception_category,
            "profiler_token": profiler_token,
            "is_framefox_exception": isinstance(exc, FramefoxException),
            **specific_context,
        }

        if not isinstance(exc, FramefoxException) or self.settings.app_env == "dev":
            clean_traceback = self._get_clean_traceback(exc.original_error if hasattr(exc, "original_error") else exc)
            clean_traceback = self._sanitize_sql_parameters(clean_traceback)
            source_info = self._parse_traceback_for_source_info(clean_traceback)

            error_context.update({"traceback": clean_traceback, "source_info": source_info})

        error_context.update({"error": "Internal Server Error", "exception": exc})

        try:
            html_content = self.template_renderer.render("debug_error.html", error_context)
            return HTMLResponse(content=html_content, status_code=getattr(exc, "status_code", 500))
        except Exception as template_error:
            self.logger.error(f"Failed to render debug template: {template_error}")
            return await self._render_fallback_error_page(request, exc)

    def _get_exception_category(self, exc: Exception) -> str:
        """Get exception category for UI styling"""
        if isinstance(exc, DatabaseException):
            return "database"
        elif isinstance(exc, AuthException):
            return "authentication"
        elif isinstance(exc, ValidationException):
            return "validation"
        elif isinstance(exc, HttpException):
            return "http"
        elif isinstance(exc, ServiceException):
            return "service"
        elif isinstance(exc, TemplateException):
            return "template"
        elif isinstance(exc, FileException):
            return "file"
        elif isinstance(exc, SettingsException):
            return "configuration"
        elif isinstance(exc, ConfigurationException):
            return "configuration"
        else:
            return "general"

    def _get_exception_specific_context(self, exc: Exception) -> dict:
        """Get specific context data based on exception type"""
        context = {}

        if isinstance(exc, TableNotFoundError):
            context.update(
                {
                    "suggestion": "Run the following command to fix this:",
                    "fix_command": "framefox database create",
                    "table_name": exc.table_name,
                    "is_database_error": True,
                }
            )
        elif isinstance(exc, DatabaseIntegrityError):
            context.update(
                {
                    "constraint": exc.constraint,
                    "suggestion": "Check for duplicate values or constraint violations",
                }
            )
        elif isinstance(exc, ValidationError):
            context.update(
                {
                    "field": exc.field,
                    "validation_message": exc.validation_message,
                    "invalid_value": exc.value,
                }
            )
        elif isinstance(exc, MultipleValidationErrors):
            context.update(
                {
                    "validation_errors": exc.errors,
                    "error_count": sum(len(field_errors) for field_errors in exc.errors.values()),
                }
            )
        elif isinstance(exc, AuthorizationError):
            context.update(
                {
                    "resource": exc.resource,
                    "action": exc.action,
                    "suggestion": "Check user permissions and roles",
                }
            )
        elif isinstance(exc, TokenExpiredError):
            context.update(
                {
                    "token_type": exc.token_type,
                    "suggestion": "Please log in again to refresh your session",
                }
            )
        elif isinstance(exc, FileUploadError):
            context.update(
                {
                    "filename": exc.filename,
                    "upload_reason": exc.reason,
                    "suggestion": "Check file format and size requirements",
                }
            )
        elif isinstance(exc, FileSizeError):
            context.update(
                {
                    "filename": exc.filename,
                    "actual_size": exc.actual_size,
                    "max_size": exc.max_size,
                    "suggestion": f"Reduce file size to under {exc.max_size} bytes",
                }
            )
        elif isinstance(exc, TimeoutError):
            context.update(
                {
                    "operation": exc.operation,
                    "timeout_seconds": exc.timeout_seconds,
                    "suggestion": "Try again later or check network connectivity",
                }
            )

        elif isinstance(exc, RateLimitExceededError):
            context.update(
                {
                    "rate_limit": exc.limit,
                    "time_window": exc.window,
                    "suggestion": "Wait before making more requests",
                }
            )
        elif isinstance(exc, TemplateNotFoundError):
            context.update(
                {
                    "template_name": exc.template_name,
                    "suggestion": f"Create template file: {exc.template_name}",
                }
            )
        elif isinstance(exc, TemplateRenderError):
            context.update(
                {
                    "template_name": exc.template_name,
                    "error_details": exc.error_details,
                    "suggestion": "Check template syntax and variable names",
                }
            )
        elif isinstance(exc, EnvironmentVariableNotFoundError):
            context.update(
                {
                    "variable_name": exc.variable_name,
                    "config_file": exc.config_file,
                    "suggestion": f"Add '{exc.variable_name}=your_value' to your .env file or set it as an environment variable",
                    "is_config_error": True,
                }
            )
        elif isinstance(exc, ConfigurationFileNotFoundError):
            context.update(
                {
                    "config_path": exc.config_path,
                    "suggestion": "Ensure the configuration directory exists and contains valid YAML files",
                    "is_config_error": True,
                }
            )
        elif isinstance(exc, InvalidConfigurationError):
            context.update(
                {
                    "config_file": exc.config_file,
                    "config_reason": exc.reason,
                    "suggestion": "Check the YAML syntax and configuration format",
                    "is_config_error": True,
                }
            )
        return context

    async def _render_production_error_page(self, request: Request, exc: Exception) -> HTMLResponse:
        """Render production-friendly error page"""
        status_code = getattr(exc, "status_code", 500)

        if isinstance(exc, (TableNotFoundError, DatabaseException)):
            error_context = {
                "request": request,
                "error_message": "The application is not properly configured. Please contact support.",
                "error_type": "Configuration Error",
            }
        elif isinstance(exc, AuthException):
            error_context = {
                "request": request,
                "error_message": "Authentication required. Please log in to continue.",
                "error_type": "Authentication Required",
            }
        elif isinstance(exc, ValidationException):
            error_context = {
                "request": request,
                "error_message": "The submitted information is invalid. Please check your input.",
                "error_type": "Invalid Input",
            }
        elif isinstance(exc, (NotFoundError, FileNotFoundError, TemplateNotFoundError)):
            error_context = {
                "request": request,
                "error_message": "The requested resource was not found.",
                "error_type": "Not Found",
            }
        else:
            error_context = {
                "request": request,
                "error_message": "An unexpected error occurred. Please try again later.",
                "error_type": "Server Error",
            }

        try:
            template_name = f"{status_code}.html" if status_code != 500 else "500.html"
            html_content = self.template_renderer.render(template_name, error_context)
            return HTMLResponse(content=html_content, status_code=status_code)
        except Exception as template_error:
            self.logger.error(f"Failed to render production error template: {template_error}")
            return await self._render_fallback_error_page(request, exc)

    async def _render_fallback_error_page(self, request: Request, exc: Exception) -> HTMLResponse:
        """Render basic HTML error page as fallback"""
        status_code = getattr(exc, "status_code", 500)
        error_code = getattr(exc, "error_code", "UNKNOWN")

        if isinstance(exc, TableNotFoundError):
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Database Setup Required</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; background: #f8f9fa; }}
                    .container {{ max-width: 800px; margin: 0 auto; }}
                    .error {{ background: #f8d7da; color: #721c24; padding: 20px; border-radius: 8px; border: 1px solid #f5c6cb; }}
                    .suggestion {{ background: #d4edda; color: #155724; padding: 15px; border-radius: 8px; margin-top: 20px; border: 1px solid #c3e6cb; }}
                    .code {{ background: #f8f9fa; padding: 8px 12px; border-radius: 4px; font-family: monospace; border: 1px solid #e9ecef; }}
                    .error-code {{ float: right; font-size: 0.9em; color: #6c757d; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="error">
                        <div class="error-code">Error Code: {error_code}</div>
                        <h1>🗄️ Database Setup Required</h1>
                        <p>Database table '<strong>{exc.table_name}</strong>' does not exist.</p>
                    </div>
                    <div class="suggestion">
                        <h3>💡 Solution</h3>
                        <p>Run the following command to fix this:</p>
                        <div class="code">framefox database create</div>
                    </div>
                </div>
            </body>
            </html>
            """
        elif isinstance(exc, ValidationError):
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Validation Error</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; background: #f8f9fa; }}
                    .container {{ max-width: 600px; margin: 0 auto; }}
                    .error {{ background: #fff3cd; color: #856404; padding: 20px; border-radius: 8px; border: 1px solid #ffeaa7; }}
                    .error-code {{ float: right; font-size: 0.9em; color: #6c757d; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="error">
                        <div class="error-code">Error Code: {error_code}</div>
                        <h1>⚠️ Validation Error</h1>
                        <p>Field '<strong>{exc.field}</strong>': {exc.validation_message}</p>
                    </div>
                </div>
            </body>
            </html>
            """
        else:
            error_message = exc.message if hasattr(exc, "message") else str(exc) if self.settings.is_debug else "An error occurred"
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Server Error</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; background: #f8f9fa; }}
                    .container {{ max-width: 600px; margin: 0 auto; }}
                    .error {{ background: #f8d7da; color: #721c24; padding: 20px; border-radius: 8px; border: 1px solid #f5c6cb; }}
                    .error-code {{ float: right; font-size: 0.9em; color: #6c757d; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="error">
                        <div class="error-code">Error Code: {error_code}</div>
                        <h1>🚫 Server Error</h1>
                        <p>{error_message}</p>
                    </div>
                </div>
            </body>
            </html>
            """

        return HTMLResponse(content=html_content, status_code=status_code)

    def _parse_traceback_for_source_info(self, traceback_str: str) -> dict:
        """Parse clean traceback for user code information"""
        if not traceback_str:
            return {
                "file": "Unknown",
                "full_file": "Unknown",
                "line": "Unknown",
                "function": "Unknown",
            }

        lines = traceback_str.split("\n")

        for line in lines:
            if 'File "' in line and "line " in line:
                if "src/" in line:
                    try:
                        file_start = line.find('File "') + 6
                        file_end = line.find('"', file_start)
                        file_path = line[file_start:file_end]

                        line_start = line.find("line ") + 5
                        line_end = line.find(",", line_start)
                        line_number = line[line_start:line_end]

                        if "in " in line:
                            func_start = line.rfind("in ") + 3
                            function_name = line[func_start:].strip()
                        else:
                            function_name = "Unknown"

                        return {
                            "file": file_path.split("/")[-1],
                            "full_file": file_path,
                            "line": line_number,
                            "function": function_name,
                        }
                    except Exception:
                        continue

        return {
            "file": "Unknown",
            "full_file": "Unknown",
            "line": "Unknown",
            "function": "Unknown",
        }
