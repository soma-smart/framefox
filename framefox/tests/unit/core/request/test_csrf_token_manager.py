from unittest.mock import AsyncMock, Mock

import pytest
from fastapi import Request

from framefox.core.request.csrf_token_manager import CsrfTokenManager

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
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
