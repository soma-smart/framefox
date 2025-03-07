from unittest.mock import AsyncMock, Mock

import pytest
from fastapi import Request, Response

from framefox.core.middleware.middlewares.request_middleware import \
    RequestMiddleware
from framefox.core.request.request_stack import RequestStack

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class TestRequestMiddleware:
    @pytest.fixture
    def mock_app(self):
        return Mock()

    @pytest.fixture
    def middleware(self, mock_app):
        return RequestMiddleware(mock_app)

    @pytest.fixture
    def mock_request(self):
        request = Mock(spec=Request)
        request.method = "GET"
        request.url = Mock()
        request.url.path = "/test"
        return request

    @pytest.fixture
    def mock_response(self):
        return Mock(spec=Response)

    @pytest.fixture
    def mock_call_next(self, mock_response):
        async_mock = AsyncMock()
        async_mock.return_value = mock_response
        return async_mock

    def test_initialization(self, middleware, mock_app):
        """Test the initialization of the middleware"""
        assert middleware.app == mock_app
        assert middleware.logger is not None

    @pytest.mark.asyncio
    async def test_dispatch(
        self, middleware, mock_request, mock_call_next, mock_response
    ):
        """Test the dispatch method"""
        response = await middleware.dispatch(mock_request, mock_call_next)

        assert RequestStack.get_request() == mock_request
        mock_call_next.assert_called_once_with(mock_request)
        assert response == mock_response

    @pytest.mark.asyncio
    async def test_dispatch_with_error(self, middleware, mock_request, mock_call_next):
        """Test error handling in dispatch"""
        mock_call_next.side_effect = Exception("Test error")

        with pytest.raises(Exception) as exc_info:
            await middleware.dispatch(mock_request, mock_call_next)

        assert str(exc_info.value) == "Test error"
        assert RequestStack.get_request() == mock_request
