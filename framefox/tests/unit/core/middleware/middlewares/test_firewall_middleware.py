import pytest
from unittest.mock import Mock, AsyncMock, patch
from fastapi import Request
from framefox.core.middleware.middlewares.firewall_middleware import FirewallMiddleware
from framefox.core.security.handlers.firewall_handler import FirewallHandler
"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: Boumaza Rayen
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
        with patch('framefox.core.middleware.middlewares.firewall_middleware.ServiceContainer') as MockServiceContainer:
            # Create a mock instance of ServiceContainer
            container_instance = Mock()
            container_instance.get.return_value = mock_handler

            # Configure the mock to return the instance
            MockServiceContainer.return_value = container_instance

            # Patch BaseHTTPMiddleware.__init__
            with patch('starlette.middleware.base.BaseHTTPMiddleware.__init__') as mock_init:
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
