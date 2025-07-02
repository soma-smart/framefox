import re
import traceback

from fastapi import Request, Response

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
from framefox.core.debug.exception.template_exception import (
    TemplateException,
    TemplateNotFoundError,
    TemplateRenderError,
)
from framefox.core.debug.exception.validation_exception import (
    MultipleValidationErrors,
    ValidationError,
    ValidationException,
)
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

    def _transform_exception(self, exc: Exception) -> Exception:
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

        if "PermissionError" in exc_type or "Permission denied" in exc_str:
            file_match = re.search(r"'([^']+)'", exc_str)
            file_path = file_match.group(1) if file_match else "unknown"
            return FilePermissionError(file_path, "access", exc)

        if "TemplateNotFound" in exc_type:
            template_match = re.search(r"template '([^']+)'", exc_str)
            template_name = template_match.group(1) if template_match else "unknown"
            return TemplateNotFoundError(template_name, exc)

        if "TemplateSyntaxError" in exc_type or "UndefinedError" in exc_type:
            template_match = re.search(r"template '([^']+)'", exc_str)
            template_name = template_match.group(1) if template_match else "unknown"
            return TemplateRenderError(template_name, str(exc), exc)

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

    def _sanitize_sql_parameters(self, text: str) -> str:
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

    def _get_exception_category(self, exc: Exception) -> str:
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
        elif isinstance(exc, ConfigurationException):
            return "configuration"
        else:
            return "general"

    def _get_exception_context(self, exc: Exception) -> dict:
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

        return context

    def collect_exception(self, exception: Exception, stack_trace: str = None) -> None:
        transformed_exception = self._transform_exception(exception)

        clean_traceback = self._get_clean_traceback(exception)
        sanitized_traceback = self._sanitize_sql_parameters(clean_traceback)

        exception_category = self._get_exception_category(transformed_exception)
        exception_context = self._get_exception_context(transformed_exception)

        exception_file = self._get_exception_file(transformed_exception)
        exception_line = self._get_exception_line(transformed_exception)

        self.exception = {
            "class": transformed_exception.__class__.__name__,
            "message": (transformed_exception.message if hasattr(transformed_exception, "message") else str(transformed_exception)),
            "original_class": exception.__class__.__name__,
            "original_message": str(exception),
            "code": getattr(transformed_exception, "error_code", "UNKNOWN"),
            "trace": sanitized_traceback,
            "file": str(exception_file) if exception_file else "Unknown",
            "line": (int(exception_line) if isinstance(exception_line, (int, str)) and str(exception_line).isdigit() else 0),
            "category": exception_category,
            "is_framefox_exception": isinstance(transformed_exception, FramefoxException),
            "context": exception_context or {},
        }

    def collect_http_error(self, status_code: int, request: Request) -> None:
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
                504: "Gateway Timeout",
            }

            self.http_error = {
                "type": "HTTP_ERROR",
                "class": f"HTTP{status_code}Error",
                "message": f"{status_code} {error_messages.get(status_code, 'HTTP Error')}",
                "code": f"HTTP_{status_code}",
                "url": str(request.url),
                "method": request.method,
                "path": request.url.path,
                "user_agent": request.headers.get("user-agent", ""),
                "referer": request.headers.get("referer", ""),
                "client_ip": request.client.host if request.client else "unknown",
                "trace": f"HTTP {status_code} error for {request.method} {request.url.path}",
                "file": "HTTP Response",
                "line": 0,
                "category": "http",
                "is_framefox_exception": False,
                "context": {
                    "status_code": status_code,
                    "suggestion": "Check the request URL and parameters",
                },
            }

    def _get_exception_file(self, exception):
        if hasattr(exception, "original_error") and exception.original_error:
            original = exception.original_error
            if hasattr(original, "__traceback__") and original.__traceback__:
                return original.__traceback__.tb_frame.f_code.co_filename

        if hasattr(exception, "__traceback__") and exception.__traceback__:
            return exception.__traceback__.tb_frame.f_code.co_filename
        return "Unknown"

    def _get_exception_line(self, exception):
        if hasattr(exception, "original_error") and exception.original_error:
            original = exception.original_error
            if hasattr(original, "__traceback__") and original.__traceback__:
                return original.__traceback__.tb_lineno

        if hasattr(exception, "__traceback__") and exception.__traceback__:
            return exception.__traceback__.tb_lineno
        return 0

    def collect(self, request: Request, response: Response) -> None:
        if hasattr(request.state, "exception"):
            stored_exception = request.state.exception

            if isinstance(stored_exception, dict):
                exception_class_name = stored_exception.get("class", "Exception")
                exception_message = stored_exception.get("message", "Unknown error")

                class TemporaryException(Exception):
                    def __init__(self, message, original_class_name):
                        super().__init__(message)
                        self.original_class_name = original_class_name

                    @property
                    def __class__(self):
                        class DynamicException(Exception):
                            __name__ = self.original_class_name

                        return DynamicException

                temp_exception = TemporaryException(exception_message, exception_class_name)
                self.collect_exception(temp_exception, stored_exception.get("trace"))
            else:
                self.collect_exception(stored_exception)

        status_code = response.status_code if hasattr(response, "status_code") else 200
        if status_code >= 400:
            self.collect_http_error(status_code, request)

        has_real_exception = self.exception is not None
        has_http_error = self.http_error is not None

        display_exception = self.exception if has_real_exception else self.http_error

        self.data = {
            "exception": display_exception,
            "status_code": status_code,
            "has_exception": has_real_exception or has_http_error,
            "exception_type": ("python_exception" if has_real_exception else "http_error" if has_http_error else None),
            "is_http_error": has_http_error and not has_real_exception,
            "is_python_exception": has_real_exception,
        }

    def reset(self):
        self.exception = None
        self.http_error = None
        self.data = {}
