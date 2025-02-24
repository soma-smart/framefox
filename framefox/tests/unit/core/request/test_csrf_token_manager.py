import pytest
from unittest.mock import Mock, AsyncMock
from fastapi import Request
from framefox.core.request.csrf_token_manager import CsrfTokenManager


"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: Boumaza Rayen
Github: https://github.com/RayenBou
"""


class TestCsrfTokenManager:
    @pytest.fixture
    def csrf_manager(self):
        """Fixture for the CSRF manager"""
        return CsrfTokenManager(prefix="test_csrf_")

    @pytest.fixture
    def mock_request(self):
        """Fixture to simulate a request"""
        request = Mock(spec=Request)
        request.cookies = {}
        request.form = AsyncMock()
        return request

    def test_init_with_custom_prefix(self):
        """Test initialization with a custom prefix"""
        custom_prefix = "custom_prefix_"
        manager = CsrfTokenManager(prefix=custom_prefix)
        assert manager.prefix == custom_prefix

    def test_generate_token(self, csrf_manager):
        """Test token generation"""
        token = csrf_manager.generate_token()

        # Check the token format
        assert token.startswith("test_csrf_")
        # Ensure there is a random part
        assert len(token) > len("test_csrf_")

        # Check that tokens are unique
        another_token = csrf_manager.generate_token()
        assert token != another_token

    def test_get_token(self, csrf_manager):
        """Test token retrieval"""
        token = csrf_manager.get_token()

        # Check the token format
        assert token.startswith("test_csrf_")
        assert len(token) > len("test_csrf_")

    @pytest.mark.asyncio
    async def test_validate_token_matching(self, csrf_manager, mock_request):
        """Test validation with matching tokens"""
        # Set up matching tokens
        test_token = "test_csrf_token123"
        mock_request.cookies = {"csrf_token": test_token}
        mock_request.form.return_value = {"csrf_token": test_token}

        # Validate the tokens
        result = await csrf_manager.validate_token(mock_request)
        assert result is True

    @pytest.mark.asyncio
    async def test_validate_token_not_matching(self, csrf_manager, mock_request):
        """Test validation with different tokens"""
        # Set up different tokens
        mock_request.cookies = {"csrf_token": "test_csrf_token123"}
        mock_request.form.return_value = {"csrf_token": "different_token"}

        # Validate the tokens
        result = await csrf_manager.validate_token(mock_request)
        assert result is False
