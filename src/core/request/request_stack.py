from fastapi import Request
from contextvars import ContextVar


_request_context: ContextVar[Request] = ContextVar("request_context")


class RequestStack:
    """
    A stack to manage request context.

    Methods:
    --------
    set_request(request: Request):
        Sets the current request in the context.

    get_request() -> Request:
        Retrieves the current request from the context.
    """

    @staticmethod
    def set_request(request: Request):
        _request_context.set(request)

    @staticmethod
    def get_request() -> Request:
        return _request_context.get()
