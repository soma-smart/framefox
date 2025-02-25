from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi import HTTPException, Request

from framefox.core.config.settings import Settings
from framefox.core.di.service_container import ServiceContainer
from framefox.core.security.authenticator.abstract_authenticator import (
    AbstractAuthenticator,
)
from framefox.core.security.passport.passport import Passport

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: Boumaza Rayen
Github: https://github.com/RayenBou
"""


class ConcreteAuthenticator(AbstractAuthenticator):
    """Concrete implementation of AbstractAuthenticator for testing"""

    async def authenticate(self, request: Request) -> Passport:
        return self.test_passport if hasattr(self, "test_passport") else None


class TestAbstractAuthenticator:
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
    def mock_request(self):
        """Fixture for FastAPI request"""
        return Mock(spec=Request)

    @pytest.fixture
    def mock_passport(self):
        """Fixture for Passport"""
        passport = Mock(spec=Passport)
        passport.authenticate_user = AsyncMock(return_value=True)
        return passport

    @pytest.fixture
    def authenticator(self, mock_container):
        """Fixture for ConcreteAuthenticator instance"""
        with patch(
            "framefox.core.security.authenticator.abstract_authenticator.ServiceContainer",
            return_value=mock_container,
        ):
            return ConcreteAuthenticator()

    @pytest.mark.asyncio
    async def test_successful_authentication(
        self, authenticator, mock_request, mock_passport
    ):
        """Test successful authentication process"""
        # Setup
        firewall_name = "main"
        authenticator.test_passport = mock_passport
        provider_info = ("UserRepository", "email")

        # Mock entity user provider
        authenticator.entity_user_provider.get_repository_and_property = Mock(
            return_value=provider_info
        )

        # Execute
        result = await authenticator.authenticate_request(mock_request, firewall_name)

        # Assert
        assert result == mock_passport
        assert result.provider_info == {
            "repository": provider_info[0],
            "property": provider_info[1],
        }
        mock_passport.authenticate_user.assert_called_once()

    @pytest.mark.asyncio
    async def test_failed_authentication_no_passport(self, authenticator, mock_request):
        """Test authentication when no passport is returned"""
        # Setup
        firewall_name = "main"
        authenticator.test_passport = None

        # Execute
        result = await authenticator.authenticate_request(mock_request, firewall_name)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_authentication_with_http_exception(
        self, authenticator, mock_request
    ):
        """Test authentication when HTTP exception occurs"""
        # Setup
        firewall_name = "main"
        authenticator.authenticate = AsyncMock(
            side_effect=HTTPException(status_code=401, detail="Unauthorized")
        )

        # Execute
        result = await authenticator.authenticate_request(mock_request, firewall_name)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_authentication_with_no_provider_info(
        self, authenticator, mock_request, mock_passport
    ):
        """Test authentication when no provider info is available"""
        # Setup
        firewall_name = "main"
        authenticator.test_passport = mock_passport
        authenticator.entity_user_provider.get_repository_and_property = Mock(
            return_value=None
        )

        # Execute
        result = await authenticator.authenticate_request(mock_request, firewall_name)

        # Assert
        assert result == mock_passport
        assert result.provider_info is None
        mock_passport.authenticate_user.assert_called_once()
