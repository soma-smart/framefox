from unittest.mock import Mock

import pytest

from framefox.core.config.settings import Settings
from framefox.core.security.access_manager import AccessManager

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class TestAccessManager:
    @pytest.fixture
    def mock_settings(self):
        """Fixture for settings"""
        settings = Mock(spec=Settings)
        settings.access_control = [
            {"path": r"^/admin.*", "roles": ["ROLE_ADMIN"]},
            {"path": r"^/api/users.*", "roles": ["ROLE_USER", "ROLE_ADMIN"]},
            {"path": r"^/public.*", "roles": "PUBLIC"},
            {"path": r"^/mixed.*", "roles": ["ROLE_USER", "ROLE_EDITOR"]},
        ]
        return settings

    @pytest.fixture
    def access_manager(self, mock_settings):
        """Fixture for AccessManager"""
        return AccessManager(mock_settings)

    def test_get_required_roles_admin_path(self, access_manager):
        """Test required roles for an admin path"""
        roles = access_manager.get_required_roles("/admin/dashboard")
        assert roles == ["ROLE_ADMIN"]

    def test_get_required_roles_multiple_roles(self, access_manager):
        """Test required roles for a path with multiple roles"""
        roles = access_manager.get_required_roles("/api/users/profile")
        assert set(roles) == {"ROLE_USER", "ROLE_ADMIN"}

    def test_get_required_roles_single_string_role(self, access_manager):
        """Test required roles when defined as a string"""
        roles = access_manager.get_required_roles("/public/index")
        assert roles == ["PUBLIC"]

    def test_get_required_roles_no_match(self, access_manager):
        """Test required roles for a path with no match"""
        roles = access_manager.get_required_roles("/unknown/path")
        assert roles == []

    def test_is_allowed_with_matching_role(self, access_manager):
        """Test authorization with a matching role"""
        user_roles = ["ROLE_USER", "ROLE_EDITOR"]
        required_roles = ["ROLE_USER", "ROLE_ADMIN"]
        assert access_manager.is_allowed(user_roles, required_roles) is True

    def test_is_allowed_with_no_matching_role(self, access_manager):
        """Test authorization without a matching role"""
        user_roles = ["ROLE_USER"]
        required_roles = ["ROLE_ADMIN"]
        assert access_manager.is_allowed(user_roles, required_roles) is False

    def test_is_allowed_with_empty_required_roles(self, access_manager):
        """Test authorization with no required roles"""
        user_roles = ["ROLE_USER"]
        required_roles = []
        assert access_manager.is_allowed(user_roles, required_roles) is False

    def test_is_allowed_with_empty_user_roles(self, access_manager):
        """Test authorization with no user roles"""
        user_roles = []
        required_roles = ["ROLE_ADMIN"]
        assert access_manager.is_allowed(user_roles, required_roles) is False

    def test_complex_path_matching(self, access_manager):
        """Test complex path matching"""
        test_cases = [
            ("/admin", ["ROLE_ADMIN"]),
            ("/admin/users/1", ["ROLE_ADMIN"]),
            ("/api/users/search", ["ROLE_USER", "ROLE_ADMIN"]),
            ("/public/assets/img.jpg", ["PUBLIC"]),
            ("/mixed/content", ["ROLE_USER", "ROLE_EDITOR"]),
            ("/unprotected", []),
        ]

        for path, expected_roles in test_cases:
            roles = access_manager.get_required_roles(path)
            assert set(roles) == set(expected_roles)
