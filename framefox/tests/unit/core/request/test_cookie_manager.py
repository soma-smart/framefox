from unittest.mock import Mock

import pytest
from fastapi.responses import Response

from framefox.core.config.settings import Settings
from framefox.core.request.cookie_manager import CookieManager

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class TestCookieManager:
    @pytest.fixture
    def mock_settings(self):
        """Fixture for settings"""
        settings = Mock(spec=Settings)
        settings.cookie_max_age = 3600
        settings.cookie_http_only = True
        settings.cookie_secure = True
        settings.cookie_same_site = "lax"
        settings.cookie_path = "/"
        return settings

    @pytest.fixture
    def cookie_manager(self, mock_settings):
        """Fixture for CookieManager"""
        return CookieManager(mock_settings)

    @pytest.fixture
    def mock_response(self):
        """Fixture for HTTP response"""
        return Mock(spec=Response)

    def test_set_cookie_with_default_values(self, cookie_manager, mock_response):
        """Test setting a cookie with default values"""
        cookie_manager.set_cookie(mock_response, "test_key", "test_value")

        mock_response.set_cookie.assert_called_once_with(
            key="test_key",
            value="test_value",
            max_age=cookie_manager.settings.cookie_max_age,
            expires=None,
            httponly=cookie_manager.settings.cookie_http_only,
            secure=cookie_manager.settings.cookie_secure,
            samesite=cookie_manager.settings.cookie_same_site,
            path=cookie_manager.settings.cookie_path,
        )

    def test_set_cookie_with_custom_values(self, cookie_manager, mock_response):
        """Test setting a cookie with custom values"""
        custom_max_age = 7200
        custom_expires = "Wed, 21 Oct 2023 07:28:00 GMT"
        custom_secure = False

        cookie_manager.set_cookie(
            mock_response,
            "test_key",
            "test_value",
            max_age=custom_max_age,
            expires=custom_expires,
            secure=custom_secure,
        )

        mock_response.set_cookie.assert_called_once_with(
            key="test_key",
            value="test_value",
            max_age=custom_max_age,
            expires=custom_expires,
            httponly=cookie_manager.settings.cookie_http_only,
            secure=custom_secure,
            samesite=cookie_manager.settings.cookie_same_site,
            path=cookie_manager.settings.cookie_path,
        )

    def test_delete_cookie(self, cookie_manager, mock_response):
        """Test deleting a cookie"""
        cookie_manager.delete_cookie(mock_response, "test_key")

        mock_response.delete_cookie.assert_called_once_with(key="test_key", path=cookie_manager.settings.cookie_path)

    def test_set_cookie_with_empty_values(self, cookie_manager, mock_response):
        """Test setting a cookie with empty values"""
        cookie_manager.set_cookie(mock_response, "", "")

        mock_response.set_cookie.assert_called_once_with(
            key="",
            value="",
            max_age=cookie_manager.settings.cookie_max_age,
            expires=None,
            httponly=cookie_manager.settings.cookie_http_only,
            secure=cookie_manager.settings.cookie_secure,
            samesite=cookie_manager.settings.cookie_same_site,
            path=cookie_manager.settings.cookie_path,
        )
