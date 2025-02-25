from unittest.mock import Mock

import pytest
from fastapi import Request

from framefox.core.security.exceptions.invalid_csrf_token_exception import (
    InvalidCsrfTokenException,
)
from framefox.core.security.passport.csrf_token_badge import CsrfTokenBadge

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class TestCsrfTokenBadge:
    @pytest.fixture
    def mock_request(self):
        """Fixture for FastAPI request"""
        request = Mock(spec=Request)
        request.cookies = {}
        return request

    @pytest.fixture
    def csrf_token(self):
        """Fixture for CSRF token"""
        return "test_csrf_token_123"

    @pytest.fixture
    def csrf_badge(self, csrf_token):
        """Fixture for CsrfTokenBadge instance"""
        return CsrfTokenBadge(csrf_token)

    def test_init_csrf_token_badge(self, csrf_token):
        """Test CsrfTokenBadge initialization"""
        badge = CsrfTokenBadge(csrf_token)
        assert badge.token == csrf_token

    def test_validate_csrf_token_success(self, csrf_badge, mock_request):
        """Test successful CSRF token validation"""
        # Setup
        mock_request.cookies["csrf_token"] = "test_csrf_token_123"

        # Execute & Assert
        assert csrf_badge.validate_csrf_token(mock_request) is True

    def test_validate_csrf_token_failure(self, csrf_badge, mock_request):
        """Test CSRF token validation failure"""
        # Setup
        mock_request.cookies["csrf_token"] = "invalid_token"

        # Execute & Assert
        with pytest.raises(InvalidCsrfTokenException):
            csrf_badge.validate_csrf_token(mock_request)

    def test_validate_csrf_token_missing(self, csrf_badge, mock_request):
        """Test CSRF token validation with missing token"""
        # Execute & Assert
        with pytest.raises(InvalidCsrfTokenException):
            csrf_badge.validate_csrf_token(mock_request)

    def test_validate_csrf_token_empty(self, csrf_badge, mock_request):
        """Test CSRF token validation with empty token"""
        # Setup
        mock_request.cookies["csrf_token"] = ""

        # Execute & Assert
        with pytest.raises(InvalidCsrfTokenException):
            csrf_badge.validate_csrf_token(mock_request)
