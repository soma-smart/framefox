import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
import jwt
from framefox.core.security.token_manager import TokenManager
from framefox.core.config.settings import Settings
from framefox.core.di.service_container import ServiceContainer

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: Boumaza Rayen
Github: https://github.com/RayenBou
"""


class TestTokenManager:
    @pytest.fixture
    def mock_settings(self):
        """Fixture for settings configuration"""
        settings = Mock(spec=Settings)
        settings.cookie_secret_key = "test_secret_key"
        return settings

    @pytest.fixture
    def mock_container(self, mock_settings):
        """Fixture for service container"""
        container = Mock(spec=ServiceContainer)
        container.get.return_value = mock_settings
        return container

    @pytest.fixture
    def token_manager(self, mock_container):
        """Fixture for TokenManager instance"""
        with patch('framefox.core.security.token_manager.ServiceContainer', return_value=mock_container):
            return TokenManager()

    @pytest.fixture
    def mock_user(self):
        """Fixture for mock user"""
        user = Mock()
        user.email = "test@example.com"
        return user

    def test_create_token(self, token_manager, mock_user):
        """Test token creation with valid user data"""
        # Test data
        firewall_name = "main"
        roles = ["ROLE_USER", "ROLE_ADMIN"]

        # Create token
        token = token_manager.create_token(mock_user, firewall_name, roles)

        # Decode and verify token
        decoded = jwt.decode(
            token,
            token_manager.settings.cookie_secret_key,
            algorithms=[token_manager.algorithm]
        )

        # Verify token contents
        assert decoded["email"] == mock_user.email
        assert decoded["firewallname"] == firewall_name
        assert decoded["roles"] == roles
        assert "exp" in decoded

    def test_decode_valid_token(self, token_manager):
        """Test decoding a valid token"""
        # Create payload
        payload = {
            "email": "test@example.com",
            "firewallname": "main",
            "roles": ["ROLE_USER"],
            "exp": datetime.utcnow() + timedelta(hours=1)
        }

        # Create token
        token = jwt.encode(
            payload,
            token_manager.settings.cookie_secret_key,
            algorithm=token_manager.algorithm
        )

        # Decode token
        decoded = token_manager.decode_token(token)

        assert decoded["email"] == payload["email"]
        assert decoded["firewallname"] == payload["firewallname"]
        assert decoded["roles"] == payload["roles"]

    def test_decode_expired_token(self, token_manager):
        """Test decoding an expired token"""
        # Create expired payload
        payload = {
            "email": "test@example.com",
            "firewallname": "main",
            "roles": ["ROLE_USER"],
            "exp": datetime.utcnow() - timedelta(hours=1)
        }

        # Create token
        token = jwt.encode(
            payload,
            token_manager.settings.cookie_secret_key,
            algorithm=token_manager.algorithm
        )

        # Attempt to decode expired token
        decoded = token_manager.decode_token(token)
        assert decoded is None

    def test_decode_invalid_token(self, token_manager):
        """Test decoding an invalid token"""
        # Test with invalid token
        invalid_token = "invalid.token.string"
        decoded = token_manager.decode_token(invalid_token)
        assert decoded is None

    def test_token_algorithm_configuration(self, token_manager):
        """Test token algorithm configuration"""
        assert token_manager.algorithm == "HS256"
