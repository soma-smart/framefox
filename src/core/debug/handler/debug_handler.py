from fastapi import Request
from fastapi.responses import HTMLResponse
from src.core.debug.exception.debug_exception import DebugException


class DebugHandler:
    @staticmethod
    async def debug_exception_handler(
        request: Request, exc: DebugException
    ) -> HTMLResponse:
        return HTMLResponse(content=exc.content, status_code=200)
