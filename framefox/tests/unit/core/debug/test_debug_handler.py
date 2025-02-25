import pytest
from fastapi import Request
from fastapi.responses import HTMLResponse

from framefox.core.debug.exception.debug_exception import DebugException
from framefox.core.debug.handler.debug_handler import DebugHandler

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: Boumaza Rayen
Github: https://github.com/RayenBou
"""


class TestDebugHandler:
    @pytest.fixture
    def mock_request(self):
        return Request(
            scope={
                "type": "http",
                "headers": [],
                "method": "GET",
                "path": "/",
                "query_string": b"",
                "client": ("127.0.0.1", 8000),
            }
        )

    @pytest.mark.asyncio
    async def test_debug_exception_handler(self, mock_request):

        test_content = "<html><body>Test Debug Content</body></html>"
        exception = DebugException(content=test_content)

        response = await DebugHandler.debug_exception_handler(mock_request, exception)
        assert isinstance(response, HTMLResponse)
        assert response.status_code == 200
        assert response.body.decode() == test_content

    @pytest.mark.asyncio
    async def test_debug_exception_handler_with_empty_content(self, mock_request):
        exception = DebugException(content="")
        response = await DebugHandler.debug_exception_handler(mock_request, exception)

        assert isinstance(response, HTMLResponse)
        assert response.status_code == 200
        assert response.body.decode() == ""
