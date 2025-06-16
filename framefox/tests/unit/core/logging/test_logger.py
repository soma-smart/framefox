import logging
from pathlib import Path
from unittest.mock import patch

import pytest

from framefox.core.logging.logger import Logger

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class TestLogger:
    @pytest.fixture
    def logger_instance(self):
        with patch("logging.config.dictConfig") as mock_dict_config:
            logger = Logger()
            yield logger, mock_dict_config

    def test_logger_initialization(self, logger_instance):
        logger, mock_dict_config = logger_instance
        assert isinstance(logger.logger, logging.Logger)
        assert logger.logger.name == "Application"
        mock_dict_config.assert_called_once()

    def test_log_directory_creation(self):
        with patch("os.makedirs") as mock_makedirs:

            expected_path = Path("./var/log").resolve()
            mock_makedirs.assert_called_once_with(expected_path, exist_ok=True)

    def test_get_logger_with_name(self, logger_instance):
        logger, _ = logger_instance
        test_logger = logger.get_logger("test.logger")
        assert isinstance(test_logger, logging.Logger)
        assert test_logger.name == "test.logger"

    def test_get_logger_without_name(self, logger_instance):
        logger, _ = logger_instance
        test_logger = logger.get_logger()
        assert isinstance(test_logger, logging.Logger)
        assert test_logger.name == "Application"

    def test_logging_config_structure(self, logger_instance):
        logger, mock_dict_config = logger_instance

        # Verify that the configuration was called with the correct parameters
        config = mock_dict_config.call_args[0][0]

        # Verify the basic structure
        assert "version" in config
        assert "formatters" in config
        assert "handlers" in config
        assert "loggers" in config
        assert "root" in config

        # Verify the formatters
        assert "colored_app" in config["formatters"]
        assert "colored_server" in config["formatters"]
        assert "file" in config["formatters"]
        assert "file_sqlmodel" in config["formatters"]

        # Verify the handlers
        assert "console_app" in config["handlers"]
        assert "console_server" in config["handlers"]
        assert "file" in config["handlers"]
        assert "file_sqlmodel" in config["handlers"]

        # Verify specific loggers
        assert "Application" in config["loggers"]
        assert "uvicorn" in config["loggers"]
        assert "sqlalchemy.engine.Engine" in config["loggers"]

    @pytest.mark.parametrize(
        "logger_name,expected_handlers",
        [
            ("Application", ["console_app", "file"]),
            ("uvicorn", ["console_server", "file"]),
            ("sqlalchemy.engine.Engine", ["file_sqlmodel"]),
        ],
    )
    def test_logger_specific_configurations(
        self, logger_instance, logger_name, expected_handlers
    ):
        logger, mock_dict_config = logger_instance
        config = mock_dict_config.call_args[0][0]

        assert logger_name in config["loggers"]
        assert "handlers" in config["loggers"][logger_name]
        assert set(config["loggers"][logger_name]["handlers"]) == set(expected_handlers)

    def test_actual_logging(self, tmp_path):
        with patch("pathlib.Path.resolve") as mock_resolve:
            mock_resolve.return_value = tmp_path
            logger = Logger()
            test_logger = logger.get_logger()

            test_message = "Test log message"
            test_logger.info(test_message)

            log_file = tmp_path / "app.log"
            assert log_file.exists()
            content = log_file.read_text()
            assert "Test log message" in content
