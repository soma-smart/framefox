from unittest.mock import Mock, patch

import pytest

from framefox.core.config.settings import Settings
from framefox.core.di.service_container import ServiceContainer
from framefox.core.security.user.entity_user_provider import EntityUserProvider

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class TestEntityUserProvider:
    @pytest.fixture
    def mock_settings(self):
        """Fixture for settings"""
        settings = Mock(spec=Settings)
        settings.firewalls = {
            "main": {"provider": "user_provider"},
            "api": {"provider": "api_provider"},
            "invalid": {"provider": "invalid_provider"},
            "no_provider": {},
        }

        settings.providers = {
            "user_provider": {"entity": {"class": "src.entity.User", "property": "email"}},
            "api_provider": {"entity": {"class": "src.entity.ApiUser", "property": "api_key"}},
            "invalid_provider": {"entity": {"class": "invalid.path.User"}},
        }
        return settings

    @pytest.fixture
    def mock_container(self, mock_settings):
        """Fixture for the service container"""
        container = Mock(spec=ServiceContainer)
        container.get.return_value = mock_settings
        ServiceContainer._instance = container
        return container

    @pytest.fixture
    def user_provider(self, mock_container):
        """Fixture for the EntityUserProvider instance"""
        return EntityUserProvider()

    @pytest.mark.asyncio
    async def test_get_repository_and_property_success(self, user_provider):
        """Test successful retrieval of repository and property"""
        with patch("importlib.import_module") as mock_import:
            # Setup mock repository
            mock_repository_class = Mock()
            mock_repository_instance = Mock()
            mock_repository_class.return_value = mock_repository_instance
            mock_module = Mock()
            mock_module.UserRepository = mock_repository_class
            mock_import.return_value = mock_module

            # Execution
            result = user_provider.get_repository_and_property("main")

            # Assertions
            assert result is not None
            repository, property_name = result
            assert repository == mock_repository_instance
            assert property_name == "email"
            mock_import.assert_called_once_with("src.entity_repository")

    def test_get_repository_and_property_no_provider(self, user_provider):
        """Test with a firewall without provider"""
        result = user_provider.get_repository_and_property("no_provider")
        assert result is None

    def test_get_repository_and_property_invalid_firewall(self, user_provider):
        """Test with an invalid firewall name"""
        result = user_provider.get_repository_and_property("nonexistent")
        assert result is None

    def test_get_repository_and_property_import_error(self, user_provider):
        """Test with an import error"""
        result = user_provider.get_repository_and_property("invalid")
        assert result is None

    def test_get_repository_and_property_missing_property(self, user_provider):
        """Test with incomplete provider configuration"""
        mock_settings = user_provider.settings
        mock_settings.providers["invalid_provider"]["entity"] = {"class": "src.entity.User"}
        result = user_provider.get_repository_and_property("invalid")
        assert result is None

    @patch("importlib.import_module")
    def test_get_repository_and_property_attribute_error(self, mock_import, user_provider):
        """Test with an attribute error during import"""
        mock_import.side_effect = AttributeError("Module has no attribute")
        result = user_provider.get_repository_and_property("main")
        assert result is None
