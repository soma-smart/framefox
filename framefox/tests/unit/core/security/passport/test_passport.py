from unittest.mock import AsyncMock, Mock

import pytest

from framefox.core.security.passport.csrf_token_badge import CsrfTokenBadge
from framefox.core.security.passport.passport import Passport
from framefox.core.security.passport.password_credentials import PasswordCredentials
from framefox.core.security.passport.user_badge import UserBadge
from framefox.core.security.password.password_hasher import PasswordHasher

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class TestPassport:
    @pytest.fixture
    def mock_user_badge(self):
        """Fixture for UserBadge"""
        badge = Mock(spec=UserBadge)
        badge.get_user = AsyncMock()
        return badge

    @pytest.fixture
    def password_hasher(self):
        """Fixture for PasswordHasher"""
        return PasswordHasher()

    @pytest.fixture
    def mock_csrf_token_badge(self):
        """Fixture for CsrfTokenBadge"""
        return Mock(spec=CsrfTokenBadge)

    @pytest.fixture
    def mock_user(self, password_hasher):
        """Fixture for User with real hashed password"""
        user = Mock()
        user.password = password_hasher.hash("test_password")
        user.roles = ["ROLE_USER"]
        return user

    @pytest.fixture
    def provider_info(self):
        """Fixture for provider information"""
        return {"repository": "UserRepository", "property": "email"}

    @pytest.fixture
    def passport(self, mock_user_badge, mock_csrf_token_badge, provider_info):
        """Fixture for Passport instance"""
        password_credentials = PasswordCredentials("test_password")
        return Passport(
            mock_user_badge, password_credentials, mock_csrf_token_badge, provider_info
        )

    @pytest.mark.asyncio
    async def test_authenticate_user_with_direct_user(self, passport, mock_user):
        """Test authentication when user is directly set"""
        # Setup
        passport.user = mock_user

        # Execute
        result = await passport.authenticate_user()

        # Assert
        assert result is True
        assert passport.roles == mock_user.roles
        assert not passport.user_badge.get_user.called

    @pytest.mark.asyncio
    async def test_authenticate_user_with_database_lookup(self, passport, mock_user):
        """Test authentication with database lookup"""
        # Setup
        passport.user_badge.get_user.return_value = mock_user

        # Execute
        result = await passport.authenticate_user()

        # Assert
        assert result is True
        assert passport.roles == mock_user.roles
        passport.user_badge.get_user.assert_called_once_with("UserRepository")

    @pytest.mark.asyncio
    async def test_authenticate_user_with_invalid_password(self, passport, mock_user):
        """Test authentication with invalid password"""
        # Setup
        passport.user_badge.get_user.return_value = mock_user
        passport.password_credentials.raw_password = "wrong_password"

        # Execute
        result = await passport.authenticate_user()

        # Assert
        assert result is False
        assert not passport.roles

    @pytest.mark.asyncio
    async def test_authenticate_user_not_found(self, passport):
        """Test authentication when user is not found"""
        # Setup
        passport.user_badge.get_user.return_value = None

        # Execute
        result = await passport.authenticate_user()

        # Assert
        assert result is False
        assert not passport.roles

    @pytest.mark.asyncio
    async def test_authenticate_user_without_provider_info(
        self, mock_user_badge, mock_csrf_token_badge
    ):
        """Test authentication without provider info"""
        # Setup
        passport = Passport(
            mock_user_badge, PasswordCredentials(
                "test_password"), mock_csrf_token_badge
        )

        # Execute
        result = await passport.authenticate_user()

        # Assert
        assert result is False
        assert not passport.roles

    @pytest.mark.asyncio
    async def test_authenticate_user_without_user_badge(self, mock_csrf_token_badge):
        """Test authentication without user badge"""
        # Setup
        passport = Passport(
            None, PasswordCredentials("test_password"), mock_csrf_token_badge
        )

        # Execute
        result = await passport.authenticate_user()

        # Assert
        assert result is False
        assert not passport.roles

    @pytest.mark.asyncio
    async def test_authenticate_user_with_missing_repository(self, passport):
        """Test authentication with missing repository in provider info"""
        # Setup
        passport.provider_info = {"property": "email"}

        # Execute
        result = await passport.authenticate_user()

        # Assert
        assert result is False
        assert not passport.roles

    @pytest.mark.asyncio
    async def test_authenticate_user_with_missing_property(self, passport):
        """Test authentication with missing property in provider info"""
        # Setup
        passport.provider_info = {"repository": "UserRepository"}

        # Execute
        result = await passport.authenticate_user()

        # Assert
        assert result is False
        assert not passport.roles
