from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi import Request

from framefox.core.middleware.middlewares.firewall_middleware import FirewallMiddleware
from framefox.core.security.handlers.firewall_handler import FirewallHandler

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class TestFirewallMiddleware:
    @pytest.fixture
    def mock_request(self):
        request = Mock(spec=Request)
        request.method = "GET"
        request.url = Mock()
        request.url.path = "/test"
        request.headers = {}
        return request

    @pytest.fixture
    def mock_call_next(self):
        return AsyncMock()

    @pytest.fixture
    def mock_app(self):
        return AsyncMock()

    @pytest.fixture
    def mock_settings(self):
        settings = Mock()
        settings.access_control = True
        return settings

    @pytest.fixture
    def mock_handler(self):
        return AsyncMock(spec=FirewallHandler)

    @pytest.fixture
    def mock_container(self, mock_handler):
        container = Mock()
        container.get.return_value = mock_handler
        return container

    @pytest.fixture
    def middleware(self, mock_app, mock_settings, mock_handler):
        with patch("framefox.core.middleware.middlewares.firewall_middleware.ServiceContainer") as MockServiceContainer:
            # Create a mock instance of ServiceContainer
            container_instance = Mock()
            container_instance.get.return_value = mock_handler

            # Configure the mock to return the instance
            MockServiceContainer.return_value = container_instance

            # Patch BaseHTTPMiddleware.__init__
            with patch("starlette.middleware.base.BaseHTTPMiddleware.__init__") as mock_init:
                mock_init.return_value = None

                # Create the middleware
                middleware = FirewallMiddleware(mock_app, mock_settings)

                # Manually define the necessary attributes
                middleware.app = mock_app
                middleware.handler = mock_handler

                return middleware

    def test_initialization(self, middleware, mock_app, mock_settings):
        """Test the initialization of the middleware"""
        assert middleware.app == mock_app
        assert middleware.settings == mock_settings
        assert middleware.logger is not None
        assert isinstance(middleware.handler, AsyncMock)

    @pytest.mark.asyncio
    async def test_dispatch_with_access_control(self, middleware, mock_request, mock_call_next, mock_handler):
        """Test dispatch avec access_control activé"""
        # Setup
        mock_response = Mock()
        mock_handler.handle_request.return_value = mock_response

        # Execute
        result = await middleware.dispatch(mock_request, mock_call_next)

        # Assert
        assert result == mock_response
        mock_handler.handle_request.assert_called_once_with(mock_request, mock_call_next)

    # @pytest.mark.asyncio
    # async def test_dispatch_without_access_control(
    #     self, middleware, mock_request, mock_call_next
    # ):
    #     """Test dispatch avec access_control désactivé"""
    #     # Setup
    #     middleware.settings.access_control = False
    #     mock_response = Mock()
    #     mock_call_next.return_value = mock_response

    #     # Execute
    #     result = await middleware.dispatch(mock_request, mock_call_next)

    #     # Assert
    #     assert result == mock_response
    #     mock_call_next.assert_called_once_with(mock_request)

    @pytest.mark.asyncio
    async def test_dispatch_with_event_dispatch(self, middleware, mock_request, mock_call_next):
        """Test dispatch avec les événements"""
        # Setup
        mock_response = Mock()
        mock_call_next.return_value = mock_response

        # Patch l'event dispatcher
        with patch("framefox.core.events.event_dispatcher.EventDispatcher.dispatch") as mock_dispatch:
            # Execute
            await middleware.dispatch(mock_request, mock_call_next)

            # Assert
            # Une fois pour auth.auth_attempt et une fois pour auth.auth_result
            assert mock_dispatch.call_count == 2
            mock_dispatch.assert_any_call("auth.auth_attempt", {"request": mock_request})

    # def test_middleware_logging(self, middleware, caplog):
    #     """Test le logging du middleware"""
    #     # Setup
    #     middleware.settings.access_control = False
    #     caplog.set_level(logging.INFO)

    #     # Execute
    #     async def test():
    #         await middleware.dispatch(Mock(spec=Request), AsyncMock())

    #     import asyncio

    #     asyncio.run(test())

    #     # Assert
    #     assert "No access control rules defined." in caplog.text
