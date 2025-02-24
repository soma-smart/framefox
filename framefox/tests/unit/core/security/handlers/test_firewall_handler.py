import pytest
from unittest.mock import Mock, AsyncMock, patch
from fastapi import Request, Response
from framefox.core.security.handlers.firewall_handler import FirewallHandler
from framefox.core.security.authenticator.authenticator_interface import AuthenticatorInterface
from framefox.core.request.request_stack import RequestStack
"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: Boumaza Rayen
Github: https://github.com/RayenBou
"""


class MockAuthenticator(AuthenticatorInterface):
    """Mock authenticator for testing"""

    async def authenticate(self, request: Request):
        return self.test_passport if hasattr(self, 'test_passport') else None

    async def authenticate_request(self, request: Request, firewall_name: str):
        return await self.authenticate(request)

    def on_auth_success(self, token: str):
        return Response(status_code=302, headers={"Location": "/dashboard"})


class TestFirewallHandler:
    @pytest.fixture
    def mock_settings(self):
        """Fixture for settings configuration"""
        settings = Mock()
        settings.firewalls = {
            "main": {
                "login_path": "/login",
                "logout_path": "/logout",
                "authenticator": "test.MockAuthenticator",
                "user_provider": {
                    "entity": "src.entity.User",
                    "property": "email"
                }
            }
        }
        settings.get_firewall_config = Mock(
            return_value=settings.firewalls["main"])
        return settings

    @pytest.fixture
    def mock_dependencies(self):
        """Fixture for all dependencies"""
        return {
            "template_renderer": Mock(),
            "cookie_manager": Mock(),
            "session_manager": Mock(),
            "token_manager": Mock(),
            "csrf_manager": Mock(),
            "access_manager": Mock()
        }

    @pytest.fixture
    def firewall_handler(self, mock_settings, mock_dependencies):
        """Fixture for FirewallHandler instance"""
        with patch('importlib.import_module'), \
                patch('inspect.signature'):
            return FirewallHandler(
                settings=mock_settings,
                **mock_dependencies
            )

    @pytest.fixture(autouse=True)
    def setup_request_context(self, mock_request):
        """Fixture to automatically setup request context for all tests"""
        RequestStack.set_request(mock_request)
        yield
        RequestStack.set_request(None)

    @pytest.fixture
    def mock_request(self):
        """Fixture for request"""
        request = Mock(spec=Request)
        request.url = Mock(path="/login")
        request.method = "POST"
        request.cookies = {}
        # Ajouter la configuration de session
        request.state = Mock()
        request.state.session_data = {}
        return request

    @pytest.mark.asyncio
    async def test_handle_authentication_success(self, firewall_handler, mock_request, mock_dependencies):
        """Test successful authentication flow"""
        # Setup
        mock_passport = Mock()
        mock_passport.user = Mock(roles=["ROLE_USER"])
        mock_dependencies["csrf_manager"].validate_token = AsyncMock(
            return_value=True)
        mock_dependencies["token_manager"].create_token.return_value = "test_token"

        # Configure session state
        mock_request.state.session_data = {}
        mock_request.state.session_id = None

        # Configure authenticator
        authenticator = MockAuthenticator()
        authenticator.test_passport = mock_passport
        firewall_handler.authenticators["main"] = authenticator

        # Execute
        response = await firewall_handler.handle_authentication(mock_request, AsyncMock())

        # Assert
        assert response.status_code == 302
        assert response.headers["Location"] == "/dashboard"
        mock_dependencies["cookie_manager"].delete_cookie.assert_called_with(
            response, "csrf_token")

    @pytest.mark.asyncio
    async def test_handle_logout(self, firewall_handler, mock_request, mock_dependencies):
        """Test logout handling"""
        try:
            # Setup
            mock_request.cookies = {"session_id": "test_session"}
            mock_dependencies["session_manager"].delete_session = Mock()

            # Configure session state
            mock_request.state.session_data = {"test_key": "test_value"}
            mock_request.state.session_id = "test_session"

            # Execute
            response = await firewall_handler.handle_logout(
                mock_request,
                firewall_handler.settings.firewalls["main"],
                "main",
                AsyncMock()
            )

            # Assert
            mock_dependencies["session_manager"].delete_session.assert_called_once_with(
                "test_session")
            assert mock_dependencies["cookie_manager"].delete_cookie.call_count == 3
        finally:
            RequestStack.set_request(None)

    @pytest.mark.asyncio
    async def test_handle_get_request(self, firewall_handler, mock_dependencies):
        """Test GET request handling for login page"""
        # Setup
        mock_dependencies["csrf_manager"].generate_token.return_value = "test_csrf_token"
        mock_dependencies["template_renderer"].render.return_value = "<html>Login form</html>"

        # Execute
        response = await firewall_handler.handle_get_request(MockAuthenticator(), {})

        # Assert
        assert response.status_code == 200
        assert response.body.decode() == "<html>Login form</html>"
        mock_dependencies["cookie_manager"].set_cookie.assert_called_with(
            response=response,
            key="csrf_token",
            value="test_csrf_token"
        )

    @pytest.mark.asyncio
    async def test_handle_request_no_firewalls(self, firewall_handler, mock_request):
        """Test request handling when no firewalls are configured"""
        # Setup
        firewall_handler.settings.firewalls = None
        mock_next = AsyncMock(return_value=Response(status_code=200))

        # Execute
        response = await firewall_handler.handle_request(mock_request, mock_next)

        # Assert
        assert response.status_code == 200
        mock_next.assert_called_once_with(mock_request)

    @pytest.mark.asyncio
    async def test_handle_post_request_failed_authentication(self, firewall_handler, mock_request, mock_dependencies):
        """Test POST request handling with failed authentication"""
        # Setup
        authenticator = MockAuthenticator()
        authenticator.test_passport = None  # Simulate authentication failure

        # Execute
        response = await firewall_handler.handle_post_request(
            mock_request,
            authenticator,
            {"login_path": "/login"},
            "main"
        )

        # Assert
        assert response.status_code == 400
        assert response.body.decode() == "Authentication failed"

    @pytest.mark.asyncio
    async def test_handle_authorization_with_invalid_token(self, firewall_handler, mock_request, mock_dependencies):
        """Test authorization with invalid token"""
        # Setup
        mock_dependencies["access_manager"].get_required_roles.return_value = [
            "ROLE_ADMIN"]
        mock_dependencies["token_manager"].decode_token.return_value = None

        with patch('framefox.core.request.session.session.Session') as mock_session:
            mock_session.get.return_value = "invalid_token"

            # Execute
            response = await firewall_handler.handle_authorization(mock_request, AsyncMock())

            # Assert
            assert response.status_code == 403
            assert response.body.decode() == "Forbidden"

    @pytest.mark.asyncio
    async def test_handle_logout_json_response(self, firewall_handler, mock_request, mock_dependencies):
        """Test logout with JSON response"""
        # Setup
        mock_request.headers = {"accept": "application/json"}
        mock_request.cookies = {"session_id": "test_session"}

        # Execute
        response = await firewall_handler.handle_logout(
            mock_request,
            firewall_handler.settings.firewalls["main"],
            "other",  # Not main firewall
            AsyncMock()
        )

        # Assert
        assert response.status_code == 200
        assert "Logout successfully" in response.body.decode()
        mock_dependencies["session_manager"].delete_session.assert_called_once()

    @pytest.mark.asyncio
    async def test_load_authenticators_error(self, mock_settings, mock_dependencies):
        """Test authenticator loading with invalid configuration"""
        # Setup
        mock_settings.firewalls = {
            "error": {
                "authenticator": "invalid.path.Authenticator"
            }
        }

        # Execute
        handler = FirewallHandler(mock_settings, **mock_dependencies)

        # Assert
        assert "error" not in handler.authenticators
        assert len(handler.authenticators) == 0

    @pytest.mark.asyncio
    async def test_handle_request_auth_routes(self, firewall_handler, mock_request, mock_dependencies):
        """Test request handling for authentication routes"""
        # Setup
        mock_request.url.path = "/login"
        mock_next = AsyncMock(return_value=Response(status_code=200))
        mock_dependencies["csrf_manager"].validate_token = AsyncMock(
            return_value=True)

        # Configure authenticator
        authenticator = MockAuthenticator()
        authenticator.authenticate_request = AsyncMock()
        firewall_handler.authenticators["main"] = authenticator

        # Configure passport
        mock_passport = Mock()
        mock_passport.user = Mock(roles=["ROLE_USER"])
        authenticator.authenticate_request.return_value = mock_passport

        # Execute
        response = await firewall_handler.handle_request(mock_request, mock_next)

        # Assert
        assert response.status_code == 302

        authenticator.authenticate_request.assert_called_once_with(
            mock_request, "main")
