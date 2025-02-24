from fastapi import Request
from fastapi.responses import HTMLResponse

from framefox.core.debug.exception.debug_exception import DebugException

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: Boumaza Rayen
Github: https://github.com/RayenBou
"""


class DebugHandler:
    @staticmethod
    async def debug_exception_handler(
        request: Request, exc: DebugException
    ) -> HTMLResponse:
        return HTMLResponse(content=exc.content, status_code=200)
