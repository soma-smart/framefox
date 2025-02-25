from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi import Request, Response

from framefox.core.middleware.middlewares.session_middleware import SessionMiddleware
from framefox.core.request.cookie_manager import CookieManager
from framefox.core.request.session.session_manager import SessionManager

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class TestSessionMiddleware:
    @pytest.fixture
    def mock_app(self):
        return AsyncMock()

    @pytest.fixture
    def mock_settings(self):
        settings = Mock()
        settings.session_cookie_name = "session_id"
        settings.cookie_max_age = 3600
        return settings

    @pytest.fixture
    def mock_cookie_manager(self):
        return Mock(spec=CookieManager)

    @pytest.fixture
    def mock_session_manager(self):
        manager = Mock(spec=SessionManager)
        manager.get_session = Mock()
        manager.create_session = Mock()
        manager.update_session = Mock()
        manager.delete_session = Mock()
        return manager

    @pytest.fixture
    def middleware(
        self, mock_app, mock_settings, mock_cookie_manager, mock_session_manager
    ):
        with patch(
            "framefox.core.middleware.middlewares.session_middleware.ServiceContainer"
        ) as MockServiceContainer:
            container_instance = Mock()
            container_instance.get.side_effect = lambda x: {
                CookieManager: mock_cookie_manager,
                SessionManager: mock_session_manager,
            }[x]
            MockServiceContainer.return_value = container_instance

            with patch(
                "starlette.middleware.base.BaseHTTPMiddleware.__init__"
            ) as mock_init:
                mock_init.return_value = None
                middleware = SessionMiddleware(mock_app, mock_settings)
                middleware.app = mock_app
                # Ajout du logger
                middleware.logger = Mock()
                return middleware

    @pytest.fixture
    def mock_request(self):
        request = Mock(spec=Request)
        request.cookies = {}
        request.state = Mock()
        return request

    @pytest.fixture
    def mock_response(self):
        return Mock(spec=Response)

    def test_initialization(self, middleware, mock_app, mock_settings):
        """Test the initialization of the middleware"""
        assert middleware.app == mock_app
        assert middleware.settings == mock_settings
        assert middleware.cookie_name == "session_id"
        assert middleware.cookie_manager is not None
        assert middleware.session_manager is not None

    @pytest.mark.asyncio
    async def test_dispatch_without_session(
        self, middleware, mock_request, mock_response
    ):
        """Test dispatch without an existing session"""
        mock_call_next = AsyncMock(return_value=mock_response)

        response = await middleware.dispatch(mock_request, mock_call_next)

        assert mock_request.state.session_id is None
        assert mock_request.state.session_data == {}
        mock_call_next.assert_called_once_with(mock_request)
        assert response == mock_response

    @pytest.mark.asyncio
    async def test_dispatch_with_expired_session(
        self, middleware, mock_request, mock_session_manager
    ):
        """Test dispatch with an expired session"""
        # Configure an expired session
        expired_session = {
            "data": {"user": "test"},
            "expires_at": (datetime.now(timezone.utc) - timedelta(hours=1)).timestamp(),
        }
        mock_request.cookies = {"session_id": "expired_id"}
        mock_session_manager.get_session.return_value = expired_session

        # Mock the Response creation
        with patch("fastapi.Response") as MockResponse:
            mock_response = Mock()
            mock_response.status_code = 440
            mock_response.body = b"Session expired. Please log in again."
            MockResponse.return_value = mock_response

            response = await middleware.dispatch(mock_request, AsyncMock())

            assert response.status_code == 440
            assert "Session expired" in response.body.decode()
            mock_session_manager.delete_session.assert_called_once_with(
                "expired_id")

    def test_cleanup_expired_sessions(self, middleware, mock_session_manager):
        """Test the cleanup of expired sessions"""
        middleware.session_manager.cleanup_expired_sessions()
        mock_session_manager.cleanup_expired_sessions.assert_called_once()
