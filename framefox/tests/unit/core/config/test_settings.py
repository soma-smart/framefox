from unittest.mock import mock_open, patch

import pytest

from framefox.core.config.settings import Settings

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class TestSettings:
    @pytest.fixture
    def mock_yaml_config(self):
        return """
        database:
            url: "postgresql://${DB_USER}:${DB_PASSWORD}@localhost/test"
        security:
            access_control:
                - role: "ROLE_USER"
        application:
            openapi_url: "/docs"
            controllers:
                dir: "controllers"
        """

    @pytest.fixture
    def settings_with_mocked_config(self, mock_yaml_config):
        with patch("os.path.exists") as mock_exists, patch(
            "builtins.open", mock_open(read_data=mock_yaml_config)
        ), patch("os.listdir") as mock_listdir, patch("os.getenv") as mock_getenv:

            mock_exists.return_value = True
            mock_listdir.return_value = ["config.yml"]
            mock_getenv.side_effect = lambda key, default=None: {
                "APP_ENV": "dev",
                "DB_USER": "test_user",
                "DB_PASSWORD": "test_pass",
            }.get(key, default)

            yield Settings()

    # def test_env_variables_replacement(self, settings_with_mocked_config):
    #     expected_url = "postgresql://test_user:test_pass@localhost/test"
    #     assert settings_with_mocked_config.database_url == expected_url

    def test_debug_mode_in_dev(self, settings_with_mocked_config):
        assert settings_with_mocked_config.debug_mode is True

    def test_access_control_loading(self, settings_with_mocked_config):
        assert settings_with_mocked_config.access_control == [{"role": "ROLE_USER"}]

    def test_get_param(self, settings_with_mocked_config):
        with patch.object(
            settings_with_mocked_config,
            "config",
            {"parameters": {"custom": {"api_key": "test_key"}}},
        ):
            assert settings_with_mocked_config.get_param("custom.api_key") == "test_key"
            assert settings_with_mocked_config.get_param("invalid.path") is None

    def test_controller_dir_default(self, settings_with_mocked_config):
        assert settings_with_mocked_config.controller_dir == "controllers"

    # @pytest.mark.parametrize("env,expected", [("dev", "/docs"), ("prod", None)])
    # def test_openapi_url_per_environment(self, env, expected):
    #     with patch("os.path.exists") as mock_exists, patch(
    #         "os.getenv"
    #     ) as mock_getenv, patch(
    #         "builtins.open",
    #         mock_open(
    #             read_data="""
    #          application:
    #              openapi_url: "/docs"
    #          """
    #         ),
    #     ):

    #         mock_exists.return_value = True
    #         mock_getenv.return_value = env

    #         settings = Settings()
    #         assert settings.openapi_url == expected

    # def test_missing_config_file(self):
    #     with patch("os.path.exists") as mock_exists:
    #         mock_exists.return_value = False
    #         with pytest.raises(Exception, match="Unable to load configuration"):
    #             Settings()

    # def test_merge_dicts(self):
    #     settings = Settings()
    #     base = {"a": 1, "b": {"c": 2}}
    #     new = {"b": {"d": 3}, "e": 4}
    #     settings.merge_dicts(base, new)
    #     assert base == {"a": 1, "b": {"c": 2, "d": 3}, "e": 4}
