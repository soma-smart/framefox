import logging
import logging.config
from pathlib import Path

from framefox.core.config.settings import Settings
from framefox.core.logging.formatter.colored_sql_formatter import ColoredSQLFormatter
from framefox.core.logging.formatter.sqlmodel_formatter import SQLModelFormatter

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: Boumaza Rayen
Github: https://github.com/RayenBou
"""


class Logger:
    """
    Logger class to configure and provide application-wide logging.

    This class initializes logging configuration based on application settings,
    including log file paths, rotation, formatting, and log levels for different
    components (application, server, SQL, etc.). It provides a method to retrieve
    loggers by name or the default application logger.
    """

    def __init__(self):
        self.settings = Settings()
        self.configure_logging()
        self.logger = logging.getLogger("Application")

    def configure_logging(self):
        """Configure logging based on application settings and debug mode"""
        log_level = self.settings.logging_level
        log_file_path = self.settings.logging_file_path
        max_size_mb = self.settings.logging_max_size
        backup_count = self.settings.logging_backup_count

        log_file_path = Path(log_file_path).resolve()
        log_dir = log_file_path.parent
        log_dir.mkdir(parents=True, exist_ok=True)

        app_log_file = str(log_file_path)
        max_bytes = max_size_mb * 1024 * 1024

        sql_console_enabled = self.settings.database_echo
        sql_profiler_enabled = self.settings.database_echo_for_profiler

        color_formatter_app = {
            "()": "colorlog.ColoredFormatter",
            "format": "%(white)s[%(reset)s%(green)sApplication%(reset)s%(white)s]%(reset)s %(asctime)s | %(log_color)s%(levelname)s%(reset)s | %(yellow)s%(name)s%(reset)s  %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
            "log_colors": {
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold_red",
            },
        }

        color_formatter_server = {
            "()": "colorlog.ColoredFormatter",
            "format": "%(white)s[%(reset)s%(cyan)sServer%(reset)s%(white)s]%(reset)s %(asctime)s | %(log_color)s%(levelname)s%(reset)s | %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
            "log_colors": {
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold_red",
            },
        }

        color_formatter_sql = {
            "()": ColoredSQLFormatter,
            "format": "%(white)s[%(reset)s%(green)sApplication%(reset)s%(white)s]%(reset)s %(asctime)s | %(log_color)s%(levelname)s%(reset)s | %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
            "log_colors": {
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold_red",
            },
        }

        file_formatter = {
            "format": "[%(levelname)s][%(asctime)s][%(name)s] %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }

        file_sql_formatter = {
            "()": SQLModelFormatter,
            "format": "[%(levelname)s][%(asctime)s][%(name)s] %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }

        sql_handlers = ["app_file"]
        
        if self.settings.is_debug and sql_console_enabled:
            sql_handlers.append("console_sql")

        logging_config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "colored_app": color_formatter_app,
                "colored_server": color_formatter_server,
                "colored_sql": color_formatter_sql,
                "file": file_formatter,
                "file_sql": file_sql_formatter,
            },
            "handlers": {
                "console_app": {
                    "class": "logging.StreamHandler",
                    "formatter": "colored_app",
                    "level": "WARNING" if not self.settings.is_debug else log_level,
                },
                "console_server": {
                    "class": "logging.StreamHandler",
                    "formatter": "colored_server",
                    "level": "WARNING" if not self.settings.is_debug else log_level,
                },
                "console_sql": {
                    "class": "logging.StreamHandler",
                    "formatter": "colored_sql",
                    "level": "INFO",
                },
                "app_file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "formatter": "file_sql",
                    "level": "INFO",
                    "filename": app_log_file,
                    "maxBytes": max_bytes,
                    "backupCount": backup_count,
                    "encoding": "utf8",
                },
            },
            "root": {
                "handlers": ["console_app", "app_file"],
                "level": "INFO",
            },
            "loggers": {
                "Application": {
                    "handlers": ["console_app", "app_file"],
                    "level": "INFO",
                    "propagate": False,
                },
                "PROFILER": {
                    "handlers": ["console_app", "app_file"],
                    "level": log_level,
                    "propagate": False,
                },
                "KERNEL": {
                    "handlers": ["console_app", "app_file"],
                    "level": "INFO",
                    "propagate": False,
                },
                "uvicorn.access": {
                    "handlers": ["app_file"],
                    "level": "WARNING",
                    "propagate": False,
                },
                "uvicorn.error": {
                    "handlers": ["console_server", "app_file"],
                    "level": "WARNING",
                    "propagate": False,
                },
                "sqlalchemy.engine.Engine": {
                    "handlers": sql_handlers,
                    "level": "INFO" if sql_profiler_enabled else "WARNING",
                    "propagate": False,
                },
                "sqlmodel": {
                    "handlers": sql_handlers,
                    "level": "INFO" if sql_profiler_enabled else "WARNING",
                    "propagate": False,
                },
                "sqlalchemy.dialects": {
                    "handlers": ["app_file"],
                    "level": "ERROR",
                    "propagate": False,
                },
                "sqlalchemy.pool": {
                    "handlers": ["app_file"],
                    "level": "ERROR",
                    "propagate": False,
                },
                "python_multipart": {
                    "handlers": ["app_file"],
                    "level": "WARNING",
                    "propagate": False,
                },
                "passlib": {
                    "handlers": ["app_file"],
                    "level": "WARNING",
                    "propagate": False,
                },
                "fastapi": {
                    "handlers": ["console_app", "app_file"],
                    "level": "WARNING",
                    "propagate": False,
                },
                "starlette": {
                    "handlers": ["console_app", "app_file"],
                    "level": "WARNING",
                    "propagate": False,
                },
            },
        }

        logging.config.dictConfig(logging_config)
