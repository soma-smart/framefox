import logging
import uuid
from contextvars import ContextVar
from typing import Any, Dict, Optional

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""
request_id: ContextVar[str] = ContextVar("request_id", default="")
request_context: ContextVar[Dict[str, Any]] = ContextVar("request_context", default={})


class ContextLogger:
    """
    Logger with context support to easily trace logs belonging to the same HTTP request.
    Provides methods to set and get request IDs and context values, and to retrieve a logger
    that automatically injects contextual information into log records.
    """

    @staticmethod
    def set_request_id(req_id: Optional[str] = None) -> str:
        if req_id is None:
            req_id = str(uuid.uuid4())
        request_id.set(req_id)
        return req_id

    @staticmethod
    def get_request_id() -> str:
        return request_id.get()

    @staticmethod
    def set_context_value(key: str, value: Any) -> None:
        context = request_context.get().copy()
        context[key] = value
        request_context.set(context)

    @staticmethod
    def get_context() -> Dict[str, Any]:
        return request_context.get()

    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        logger = logging.getLogger(name)

        original_debug = logger.debug
        original_info = logger.info
        original_warning = logger.warning
        original_error = logger.error
        original_critical = logger.critical

        def add_context_info(func, *args, **kwargs):
            extra = kwargs.get("extra", {})
            req_id = ContextLogger.get_request_id()
            if req_id:
                extra["request_id"] = req_id

            context = ContextLogger.get_context()
            for key, value in context.items():
                extra[key] = value

            kwargs["extra"] = extra
            return func(*args, **kwargs)

        logger.debug = lambda *args, **kwargs: add_context_info(
            original_debug, *args, **kwargs
        )
        logger.info = lambda *args, **kwargs: add_context_info(
            original_info, *args, **kwargs
        )
        logger.warning = lambda *args, **kwargs: add_context_info(
            original_warning, *args, **kwargs
        )
        logger.error = lambda *args, **kwargs: add_context_info(
            original_error, *args, **kwargs
        )
        logger.critical = lambda *args, **kwargs: add_context_info(
            original_critical, *args, **kwargs
        )

        return logger
