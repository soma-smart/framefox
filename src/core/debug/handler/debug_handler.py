from fastapi import Request
from fastapi.responses import HTMLResponse
<<<<<<< Updated upstream:src/core/debug/handler/debug_handler.py
<<<<<<< Updated upstream:src/core/debug/handler/debug_handler.py
from src.core.debug.exception.debug_exception import DebugException
=======
=======
>>>>>>> Stashed changes:framefox/core/debug/handler/debug_handler.py

from framefox.core.debug.exception.debug_exception import DebugException
>>>>>>> Stashed changes:framefox/core/debug/handler/debug_handler.py


class DebugHandler:
    @staticmethod
    async def debug_exception_handler(
        request: Request, exc: DebugException
    ) -> HTMLResponse:
        return HTMLResponse(content=exc.content, status_code=200)
